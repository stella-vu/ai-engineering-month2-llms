import json

import ollama
from pydantic import ValidationError

from app.config import LLM_MODEL
from app.schemas import ExtractedMetadata
from app.currency_resolver import CurrencyResolver
from app.status_resolver import StatusResolver
from app.tax_resolver import TaxResolver
from app.party_resolver import PartyResolver
from app.document_classifier import DocumentClassifier


class MetadataExtractor:
    """
    Extracts accounting document metadata from parsed text using a local LLM.

    Output is validated with Pydantic before being used by the app.
    """

    def __init__(self, model: str = LLM_MODEL) -> None:
        self.model = model
        self.currency_resolver = CurrencyResolver()
        self.status_resolver = StatusResolver()
        self.tax_resolver = TaxResolver()
        self.party_resolver = PartyResolver()
        self.document_classifier = DocumentClassifier()

    def extract(self, document_text: str) -> ExtractedMetadata:
        if not document_text or not document_text.strip():
            raise ValueError("Document text cannot be empty.")

        classified_document_type = self.document_classifier.classify(document_text)

        prompt = self._build_prompt(
            document_text=document_text,
            classified_document_type=classified_document_type,
            )

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract accounting document metadata. "
                        "Return only valid JSON. Do not include markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            format="json",
        )

        content = response["message"]["content"]

        try:
            data = json.loads(content)
            data = self._clean_llm_data(data)
            metadata = ExtractedMetadata.model_validate(data)
            
            metadata.document_type = classified_document_type

            metadata.currency = self.currency_resolver.resolve(
                document_text=document_text
            )
            
            metadata.status = self.status_resolver.resolve(
                document_text=document_text,
                document_type=metadata.document_type
            )

            metadata.gst = self.tax_resolver.resolve_gst(
                document_text=document_text,
                llm_gst=metadata.gst,
            )

            metadata.supplier = self.party_resolver.resolve_supplier(
                document_text=document_text,
                llm_supplier=metadata.supplier
            )

            metadata.client = self.party_resolver.resolve_client(
                document_text=document_text,
                llm_client=metadata.client,
            )


            return metadata

        except json.JSONDecodeError as error:
            raise ValueError(f"LLM did not return valid JSON: {content}") from error

        except ValidationError as error:
            raise ValueError(f"LLM JSON did not match ExtractedMetadata schema: {error}") from error

    def _build_prompt(self, document_text: str, classified_document_type) -> str:
        return f"""
The document has already been classified as: {classified_document_type}
Use this document type unless the text clearly proves it is wrong.

Extract metadata from this accounting document.

Return JSON with exactly these keys:
{{
  "document_type": "invoice | receipt | bank_statement | tax_document | contract | other",
  "supplier": "string or null",
  "client": "string or null",
  "document_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "amount": 0.0,
  "currency": "AUD | USD | VND | OTHER",
  "gst": 0.0,
  "status": "paid | unpaid | overdue | partial | n/a | unknown"
}}
Document type rule:
- The system classified this document as "{classified_document_type}".
- Use this value for document_type unless there is very strong evidence it is wrong.

Rules:
- Use real JSON null for missing values.
- Do not use the string "null".
- Do not use "None", "N/A", or "unknown" for date fields.- For invoices, amount should be the final total amount.
- For receipts, amount should be the paid total.
- For tax/GST fields, use the tax/GST amount if shown.
- Payment Instructions, bank details, ACH details, remittance details, or "Thank you for your business" do NOT mean the invoice is paid.
- Only use "paid" if the document clearly says paid, payment received, paid by card, paid in full, or receipt.
- If document_type is "invoice", due_date exists, and there is no clear paid confirmation, status must be "unpaid".
- If the document shows "Total" and payment instructions, treat it as unpaid unless clearly stated otherwise.
- Currency rules:
    - Prefer an explicit ISO currency code if shown, such as USD, AUD, VND, CAD, NZD, SGD.
    - If the document clearly says "US dollars", "United States dollars", or uses a US bank payment method such as ACH/routing number, use "USD".
    - If the document clearly says "Australian dollars", "AUD", GST with Australian business context, BAS, ATO, ABN, or Australian bank details, use "AUD".
    - If the document clearly says "Vietnamese dong" or "VND", use "VND".
    - The "$" symbol alone is not enough to decide currency.
    - If the currency is not clear, return "OTHER".
    - Do not default to AUD.

- Do not invent values.
- Return only JSON.

Document text:
{document_text}
"""
    
    def _clean_llm_data(self, data: dict) -> dict:
        """
        Converts common LLM mistakes into valid Python values before Pydantic validation.
        Example: "null" -> None
        """

        null_like_values = {"null", "none", "n/a", "unknown", ""}

        for key, value in data.items():
            if isinstance(value, str) and value.strip().lower() in null_like_values:
                data[key] = None

        return data