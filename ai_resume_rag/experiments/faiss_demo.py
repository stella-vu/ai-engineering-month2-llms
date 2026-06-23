from document_loader import load_text_file
from text_chunker import chunk_text
from vector_store import VectorStore


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

    queries = [
        "What warehouse and inventory experience does this candidate have?",
        "Does this candidate have customer service experience?",
        "What education does this candidate have?",
    ]

    for query in queries:
        results = vector_store.search(
            query=query,
            top_k=3,
        )

        print("\n" + "=" * 60)
        print("Query:")
        print(query)
        print("=" * 60)

        for result in results:
            print("\n" + "-" * 60)
            print(f"Score: {result['score']:.4f}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Source: {result['source']}")
            print("-" * 60)
            print(result["text"])


if __name__ == "__main__":
    main()