from app.retriever import DocumentRetriever
from app.schemas import DocumentType, PaymentStatus, SearchFilters


def print_results(title, results):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print("Results found:", len(results))

    for result in results:
        print("\n" + "-" * 50)
        print("Score:", round(result.score, 4))
        print("Document ID:", result.payload.document_id)
        print("Chunk ID:", result.payload.chunk_id)
        print("Type:", result.payload.document_type)
        print("Supplier:", result.payload.supplier)
        print("Client:", result.payload.client)
        print("Date:", result.payload.document_date)
        print("Due date:", result.payload.due_date)
        print("Amount:", result.payload.amount)
        print("Currency:", result.payload.currency)
        print("GST:", result.payload.gst)
        print("Status:", result.payload.status)
        print("File:", result.payload.file_name)
        print("Text preview:", result.text[:50])


def main():
    retriever = DocumentRetriever()

    unpaid_invoices = retriever.retrieve(
        query="Find unpaid invoices",
        filters=SearchFilters(
            document_type=DocumentType.INVOICE,
            status=PaymentStatus.UNPAID,
            top_k=10,
        ),
    )
    print_results("Unpaid invoices", unpaid_invoices)

    elevenlabs_documents = retriever.retrieve(
        query="Find ElevenLabs documents",
        filters=SearchFilters(
            supplier="Eleven Labs Inc.",
            top_k=10,
        ),
    )
    print_results("ElevenLabs documents", elevenlabs_documents)

    paid_receipts = retriever.retrieve(
        query="Find paid receipts",
        filters=SearchFilters(
            document_type=DocumentType.RECEIPT,
            status=PaymentStatus.PAID,
            top_k=10,
        ),
    )
    print_results("Paid receipts", paid_receipts)

    gst_documents = retriever.retrieve(
        query="Find documents with Australian GST",
        filters=SearchFilters(
            min_gst=0.01,
            top_k=10,
        ),
    )
    print_results("Australian GST documents", gst_documents)


if __name__ == "__main__":
    main()