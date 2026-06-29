import ollama

from app.config import VECTOR_SIZE, EMBEDDING_MODEL

    
class OllamaEmbedder:
    """
    Real local embedding model using Ollama.

    Text -> semantic vector.
    """

    def __init__(self, model: str = EMBEDDING_MODEL) -> None:
        self.model = model

    def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        response = ollama.embed(
            model=self.model,
            input=text,
        )

        vector = response["embeddings"][0]

        if len(vector) != VECTOR_SIZE:
            raise ValueError(
                f"Embedding size mismatch. "
                f"Expected {VECTOR_SIZE}, got {len(vector)}."
            )

        return vector

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        for text in texts:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty.")

        response = ollama.embed(
            model=self.model,
            input=texts,
        )

        vectors = response["embeddings"]

        for vector in vectors:
            if len(vector) != VECTOR_SIZE:
                raise ValueError(
                    f"Embedding size mismatch. "
                    f"Expected {VECTOR_SIZE}, got {len(vector)}."
                )

        return vectors