from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    Range,
    VectorParams,
)

from app.config import COLLECTION_NAME, QDRANT_URL, VECTOR_SIZE
from app.schemas import DocumentChunk, SearchFilters, SearchResult


class QdrantStore:
    """
    Handles all Qdrant database operations.
    """

    def __init__(self) -> None:
        self.client = QdrantClient(url=QDRANT_URL)

    def recreate_collection(self) -> None:
        """
        Delete and recreate collection.
        Use this for learning/testing only.
        Later, production ingestion should not delete existing data.
        """

        if self.client.collection_exists(COLLECTION_NAME):
            self.client.delete_collection(COLLECTION_NAME)

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    def ensure_collection_exists(self) -> None:
        """
        Create collection only if it does not exist.
        Safer than recreate_collection for normal app usage.
        """

        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        vectors: list[list[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Number of chunks must match number of vectors.")

        points = []

        for chunk, vector in zip(chunks, vectors):
            point = PointStruct(
                id=chunk.point_id,
                vector=vector,
                payload=chunk.payload.model_dump(),
            )
            points.append(point)

        self.client.upsert(
            collection_name=COLLECTION_NAME,
            wait=True,
            points=points,
        )

    def search(
        self,
        query_vector: list[float],
        filters: SearchFilters | None = None,
    ) -> list[SearchResult]:
        query_filter = self._build_filter(filters)

        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=filters.top_k if filters else 5,
        )

        results = []

        for point in response.points:
            payload = point.payload or {}

            result = SearchResult(
                point_id=str(point.id),
                score=point.score,
                payload=payload,
                text=payload.get("text", ""),
            )
            results.append(result)

        return results

    def _build_filter(self, filters: SearchFilters | None) -> Filter | None:
        if filters is None:
            return None

        conditions = []

        if filters.document_type:
            conditions.append(
                FieldCondition(
                    key="document_type",
                    match=MatchValue(value=filters.document_type),
                )
            )

        if filters.supplier:
            conditions.append(
                FieldCondition(
                    key="supplier",
                    match=MatchValue(value=filters.supplier),
                )
            )

        if filters.client:
            conditions.append(
                FieldCondition(
                    key="client",
                    match=MatchValue(value=filters.client),
                )
            )

        if filters.status:
            conditions.append(
                FieldCondition(
                    key="status",
                    match=MatchValue(value=filters.status),
                )
            )

        if filters.min_gst is not None or filters.max_gst is not None:
            conditions.append(
                FieldCondition(
                    key="gst",
                    range=Range(
                        gte=filters.min_gst,
                        lte=filters.max_gst,
                    ),
                )
            )

        if filters.min_amount is not None or filters.max_amount is not None:
            conditions.append(
                FieldCondition(
                    key="amount",
                    range=Range(
                        gte=filters.min_amount,
                        lte=filters.max_amount,
                    ),
                )
            )

        if filters.start_date is not None or filters.end_date is not None:
            # Qdrant date filtering expects datetime-style string bounds.
            # We convert Python date objects into full-day UTC datetime strings.
            range_bounds = {}
            
            if filters.start_date:
                range_bounds["gte"] = f"{filters.start_date.isoformat()}T00:00:00Z"
            
            if filters.end_date:
                range_bounds["lte"] = f"{filters.end_date.isoformat()}T23:59:59Z"
            
            conditions.append(
                FieldCondition(
                    key="document_date",
                    range=range_bounds
                )
            )
        
            
        if not conditions:
            return None

        return Filter(must=conditions)