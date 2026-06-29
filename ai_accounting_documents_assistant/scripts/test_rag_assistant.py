from app.rag_assistant import RAGAssistant
from app.schemas import DocumentType, PaymentStatus, SearchFilters


def print_answer(title: str, result: dict) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")
    for source in result["sources"]:
        print(
            f"- {source['file_name']} | "
            f"{source['chunk_id']} | "
            f"{source['document_type']} | "
            f"{source['supplier']} | "
            f"score={round(source['score'], 4)}"
        )


def main():
    assistant = RAGAssistant()

    result = assistant.answer(
        question="Which invoices are unpaid?",
        filters=SearchFilters(
            document_type=DocumentType.INVOICE,
            status=PaymentStatus.UNPAID,
            top_k=6,
        ),
    )
    print_answer("Question 1: Unpaid invoices", result)

    result = assistant.answer(
        question="What documents do I have from Eleven Labs?",
        filters=SearchFilters(
            supplier="Eleven Labs Inc.",
            top_k=6,
        ),
    )
    print_answer("Question 2: ElevenLabs documents", result)

    result = assistant.answer(
        question="Which documents include Australian GST and how much GST is shown?",
        filters=SearchFilters(
            min_gst=0.01,
            top_k=6,
        ),
    )
    print_answer("Question 3: Australian GST", result)

    result = assistant.answer(
        question="Has the Eleven Labs invoice been paid?",
        filters=SearchFilters(
            supplier="Eleven Labs Inc.",
            top_k=6,
        ),
    )
    print_answer("Question 4: ElevenLabs payment status", result)


if __name__ == "__main__":
    main()