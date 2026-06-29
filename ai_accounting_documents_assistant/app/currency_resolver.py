import re

from app.schemas import Currency


class CurrencyResolver:
    """
    Resolves currency from document text using evidence-based rules.

    This avoids trusting "$" alone because $ can mean USD, AUD, CAD, NZD, SGD, etc.
    Use priority order:
    1. Explicit ISO code: USD, AUD, VND
    2. Explicit currency words: US dollars, Australian dollars, Vietnamese dong
    3. Country/payment evidence: ACH/routing = USD, ABN/BSB/ATO/GST/BAS = AUD
    4. If only "$" and no evidence: OTHER

    Important:
    - "$" alone is ambiguous.
    - GST shown as "(A$...)" does not mean the total document currency is AUD.
    """

    def resolve(
        self,
        document_text: str
    ) -> Currency:
        if not document_text or not document_text.strip():
            return Currency.OTHER

        text = document_text.lower()

        explicit_total_currency = self._resolve_explicit_total_currency(text)
        if explicit_total_currency != Currency.OTHER:
            return explicit_total_currency

        explicit_general_currency = self._resolve_explicit_currency_words(text)
        if explicit_general_currency != Currency.OTHER:
            return explicit_general_currency

        payment_context_currency = self._resolve_payment_context(text)
        if payment_context_currency != Currency.OTHER:
            return payment_context_currency

        return Currency.OTHER

    def _resolve_explicit_total_currency(self, text: str) -> Currency:
        """
        Strongest evidence:
        The amount due / amount paid / total line directly includes a currency code.
        """

        usd_patterns = [
            r"amount due\s+\$[\d,]+(?:\.\d{1,2})?\s+usd",
            r"\$[\d,]+(?:\.\d{1,2})?\s+usd\s+due",
            r"amount paid\s+\$[\d,]+(?:\.\d{1,2})?\s+usd",
            r"total\s+\$[\d,]+(?:\.\d{1,2})?\s+usd",
        ]

        aud_patterns = [
            r"amount due\s+a\$[\d,]+(?:\.\d{1,2})?",
            r"amount paid\s+a\$[\d,]+(?:\.\d{1,2})?",
            r"total\s+a\$[\d,]+(?:\.\d{1,2})?",
            r"amount due\s+\$[\d,]+(?:\.\d{1,2})?\s+aud",
            r"amount paid\s+\$[\d,]+(?:\.\d{1,2})?\s+aud",
            r"total\s+\$[\d,]+(?:\.\d{1,2})?\s+aud",
        ]

        vnd_patterns = [
            r"amount due\s+[\d,.]+\s+vnd",
            r"amount paid\s+[\d,.]+\s+vnd",
            r"total\s+[\d,.]+\s+vnd",
            r"[\d,.]+\s*₫",
        ]

        if any(re.search(pattern, text) for pattern in usd_patterns):
            return Currency.USD

        if any(re.search(pattern, text) for pattern in aud_patterns):
            return Currency.AUD

        if any(re.search(pattern, text) for pattern in vnd_patterns):
            return Currency.VND

        return Currency.OTHER

    def _resolve_explicit_currency_words(self, text: str) -> Currency:
        if re.search(r"\b(usd|us dollars?|u\.s\. dollars?|united states dollars?)\b", text):
            return Currency.USD

        if re.search(r"\b(aud|australian dollars?)\b", text):
            return Currency.AUD

        if re.search(r"\b(vnd|vietnamese dong|viet nam dong)\b", text):
            return Currency.VND

        return Currency.OTHER

    def _resolve_payment_context(self, text: str) -> Currency:
        """
        Payment context is weaker than explicit total currency.
        """

        usd_payment_markers = [
            "ach",
            "routing number",
            "routing:",
            "wire routing",
        ]

        aud_payment_markers = [
            "bsb",
            "australian bank",
            "bpay",
        ]

        if any(marker in text for marker in usd_payment_markers):
            return Currency.USD

        if any(marker in text for marker in aud_payment_markers):
            return Currency.AUD

        return Currency.OTHER