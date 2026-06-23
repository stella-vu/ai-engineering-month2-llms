import requests
import numpy as np


OLLAMA_EMBEDDING_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"


def get_embedding(text: str) -> np.ndarray:
    response = requests.post(
        OLLAMA_EMBEDDING_URL,
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text,
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return np.array(data["embedding"], dtype=np.float32)


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    dot_product = np.dot(vector_a, vector_b)

    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))