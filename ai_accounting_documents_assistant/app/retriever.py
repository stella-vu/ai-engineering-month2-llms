from app.embedder import OllamaEmbedder
from app.qdrant_store import QdrantStore
from app.schemas import RetrievedContext, SearchFilters, SearchResult


class DocumentRetriever:
    """
    High-level retrieval layer.

    Responsibilities:
    - Convert user query into embedding vector
    - Search Qdrant using vector + optional metadata filters
    - Return clean SearchResult objects
    """

    def __init__(
        self,
        embedder: OllamaEmbedder | None = None,
        store: QdrantStore | None = None,
    ) -> None:
        self.embedder = embedder or OllamaEmbedder()
        self.store = store or QdrantStore()

    def retrieve(
        self,
        query: str,
        filters: SearchFilters | None = None,
    ) -> list[SearchResult]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        query_vector = self.embedder.embed_text(query)

        results = self.store.search(
            query_vector=query_vector,
            filters=filters,
        )

        return results

    def retrieve_context(
        self,
        query: str,
        filters: SearchFilters | None = None,
    ) -> RetrievedContext:
        results = self.retrieve(
            query=query,
            filters=filters,
        )

        return RetrievedContext(
            query=query,
            filters=filters,
            results=results,
        )