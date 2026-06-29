from app.embedder import OllamaEmbedder


def main():
    embedder = OllamaEmbedder()

    text = ["Officeworks invoice for printer paper. Total amount is $650 and payment is unpaid.",
            "Receipt includes GST of $7.68 for tea, milk, snacks, and cleaning items."
            ]

    vectors = embedder.embed_texts(text)

    for vector in vectors:
        print("Embedding created successfully")
        print("Vector length:", len(vector))
        print("First 5 values:", vector[:5])


if __name__ == "__main__":
    main()