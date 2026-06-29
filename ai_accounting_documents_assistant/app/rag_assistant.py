import ollama

from app.config import LLM_MODEL
from app.retriever import DocumentRetriever
from app.schemas import RetrievedContext, SearchFilters


class RAGAssistant:
    """
    Retrieval-Augmented Generation assistant.

    Responsibilities:
    - Retrieve relevant document chunks from Qdrant
    - Build a grounded prompt
    - Ask local LLM to answer using only retrieved context
    - Return answer with sources
    """

    def __init__(
        self,
        retriever: DocumentRetriever | None = None,
        model: str = LLM_MODEL,
    ) -> None:
        self.retriever = retriever or DocumentRetriever()
        self.model = model

    def answer(
        self,
        question: str,
        filters: SearchFilters | None = None,
    ) -> dict:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        context = self.retriever.retrieve_context(
            query=question,
            filters=filters,
        )

        context = self._deduplicate_results_by_document(context)

        if not context.results:
            return {
                "answer": "I could not find relevant documents for this question.",
                "sources": [],
            }

        prompt = self._build_prompt(
            question=question,
            context=context,
        )

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an accounting document assistant. "
                        "Answer only using the provided document context. "
                        "If the answer is not in the context, say you cannot find it. "
                        "Do not invent facts."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            options={
                "temperature": 0.1,
            },
        )

        answer_text = response["message"]["content"]

        return {
            "answer": answer_text,
            "sources": self._build_sources(context),
        }

    def _build_prompt(
        self,
        question: str,
        context: RetrievedContext,
    ) -> str:
        context_blocks = []

        for index, result in enumerate(context.results, start=1):
            payload = result.payload

            context_blocks.append(
                f"""
Source {index}
File: {payload.file_name}
Document ID: {payload.document_id}
Chunk ID: {payload.chunk_id}
Document type: {payload.document_type}
Supplier: {payload.supplier}
Client: {payload.client}
Date: {payload.document_date}
Due date: {payload.due_date}
Amount: {payload.amount}
Currency: {payload.currency}
GST: {payload.gst}
Status: {payload.status}
Text:
{result.text}
"""
            )

        joined_context = "\n".join(context_blocks)

        return f"""
Question:
{question}

Document context:
{joined_context}

Instructions:
- Answer the question directly.
- Treat multiple chunks with the same Document ID as the same document.
- Do not count chunks as separate invoices, receipts, or documents.
- For structured fields, always prefer metadata over raw text.
- Structured fields include supplier, client, amount, currency, GST, dates, document type, and status.
- If raw text conflicts with metadata, mention the metadata value and say the raw text contains additional detail.
- Use raw text only to support or clarify metadata.
- If the retrieved context contains enough information, do not ask the user for clarification.
- If multiple documents are relevant, summarize them as a clear list.
- Do not claim an invoice is paid only because a receipt from the same supplier appears in the context.
- If an invoice and receipt may be related but are not explicitly linked by invoice number or document ID, say it suggests payment but needs reconciliation.
- If invoice metadata says status is unpaid and receipt metadata says paid, explain both.
- Do not write a Sources section. The app will display sources separately.
- Do not invent facts.
- Do not use outside knowledge.
"""

    def _build_sources(self, context: RetrievedContext) -> list[dict]:
        sources = []
        seen = set()

        for result in context.results:
            payload = result.payload
            key = (payload.file_name, payload.chunk_id)

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "file_name": payload.file_name,
                    "document_id": payload.document_id,
                    "chunk_id": payload.chunk_id,
                    "document_type": payload.document_type,
                    "supplier": payload.supplier,
                    "score": result.score,
                }
            )

        return sources
    
    def _deduplicate_results_by_document(
        self,
        context: RetrievedContext,
        max_chunks_per_document: int = 2,
    ) -> RetrievedContext:
        grouped_counts: dict[str, int] = {}
        deduplicated_results = []

        for result in context.results:
            document_id = result.payload.document_id
            current_count = grouped_counts.get(document_id, 0)

            if current_count >= max_chunks_per_document:
                continue

            deduplicated_results.append(result)
            grouped_counts[document_id] = current_count + 1

        context.results = deduplicated_results
        return context