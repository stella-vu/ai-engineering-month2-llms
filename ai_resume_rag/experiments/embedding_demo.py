from embedding_service import get_embedding, cosine_similarity


def main():
    query = "warehouse inventory experience"

    documents = [
        "Warehouse assistant with picking, packing, and stock control experience.",
        "Python developer skilled in FastAPI, PostgreSQL, and backend APIs.",
        "Inventory management, logistics coordination, and warehouse operations.",
        "Customer service worker with strong communication and teamwork skills.",
        "AI engineer building RAG applications with embeddings and vector search.",
    ]

    query_embedding = get_embedding(query)

    results = []

    for document in documents:
        document_embedding = get_embedding(document)

        score = cosine_similarity(query_embedding, document_embedding)

        results.append(
            {
                "document": document,
                "score": score,
            }
        )

    results = sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )

    print("\nQuery:")
    print(query)

    print("\nMost similar documents:\n")

    for index, result in enumerate(results, start=1):
        print(f"{index}. Score: {result['score']:.4f}")
        print(f"   Text: {result['document']}")
        print()


if __name__ == "__main__":
    main()