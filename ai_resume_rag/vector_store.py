import faiss
import numpy as np

from embedding_service import get_embedding


class VectorStore:
    def __init__(self):
        self.index = None
        self.metadata = []

    def build_index(self, chunks: list[str], source: str = "unknown") -> None:
        if not chunks:
            raise ValueError("No chunks provided.")

        embeddings = []
        self.metadata = []

        for chunk_id, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)

            embeddings.append(embedding)

            self.metadata.append(
                {
                    "chunk_id": chunk_id,
                    "source": source,
                    "text": chunk,
                }
            )

        embedding_matrix = np.array(embeddings, dtype=np.float32)

        faiss.normalize_L2(embedding_matrix)

        dimension = embedding_matrix.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embedding_matrix)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if self.index is None:
            raise ValueError("FAISS index has not been built yet.")

        query_embedding = get_embedding(query)

        query_matrix = np.array([query_embedding], dtype=np.float32)

        faiss.normalize_L2(query_matrix)

        scores, indices = self.index.search(query_matrix, top_k)

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            item = self.metadata[index].copy()
            item["score"] = float(score)

            results.append(item)

        return results