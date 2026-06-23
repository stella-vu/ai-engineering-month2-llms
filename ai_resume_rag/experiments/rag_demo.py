from document_loader import load_text_file
from text_chunker import chunk_text
from vector_store import VectorStore
from rag_service import answer_question


def main():
    file_path = "docs/sample_warehouse_resume.docx"

    resume_text = load_text_file(file_path)

    chunks = chunk_text(
        resume_text,
        chunk_size=700,
        chunk_overlap=120,
    )

    vector_store = VectorStore()

    vector_store.build_index(
        chunks=chunks,
        source=file_path,
    )

    questions = [
        "What warehouse and inventory experience does this candidate have?",
        "Does this candidate have customer service experience?",
        "What education does this candidate have?",
        "Does this candidate have forklift experience?",
    ]

    for question in questions:
        result = answer_question(
            question=question,
            vector_store=vector_store,
            top_k=4,
        )

        print("\n" + "=" * 60)
        print("Question:")
        print(question)
        print("=" * 60)

        print("\nAnswer:")
        print(result["answer"])

        print("\nRetrieved chunks:")
        for chunk in result["retrieved_chunks"]:
            print(
                f"- Chunk {chunk['chunk_id']} | Score: {chunk['score']:.4f}"
            )


if __name__ == "__main__":
    main()