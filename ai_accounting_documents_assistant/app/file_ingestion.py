from pathlib import Path
from uuid import uuid4

from app.chunker import TextChunker
from app.document_parser import DocumentParser
from app.embedder import OllamaEmbedder
from app.metadata_extractor import MetadataExtractor
from app.qdrant_store import QdrantStore
from app.schemas import DocumentChunk, DocumentPayload, IngestionResult


class FileIngestionPipeline:
    """
    Reusable ingestion pipeline for real document files.

    File -> parse -> extract metadata -> chunk -> embed -> Qdrant
    """

    def __init__(
        self,
        parser: DocumentParser | None = None,
        chunker: TextChunker | None = None,
        embedder: OllamaEmbedder | None = None,
        metadata_extractor: MetadataExtractor | None = None,
        store: QdrantStore | None = None,
    ) -> None:
        self.parser = parser or DocumentParser()
        self.chunker = chunker or TextChunker()
        self.embedder = embedder or OllamaEmbedder()
        self.metadata_extractor = metadata_extractor or MetadataExtractor()
        self.store = store or QdrantStore()

    def ingest_file(
        self,
        file_path: str | Path,
        document_id: str | None = None,
        recreate_collection: bool = False,
    ) -> IngestionResult:
        path = Path(file_path)

        if recreate_collection:
            self.store.recreate_collection()
        else:
            self.store.ensure_collection_exists()

        text = self.parser.parse_file(path)
        metadata = self.metadata_extractor.extract(text)
        text_chunks = self.chunker.split_text(text)

        resolved_document_id = document_id or path.stem.lower().replace("-", "_")

        chunks: list[DocumentChunk] = []

        for chunk_index, chunk_text in enumerate(text_chunks):
            chunk_id = f"{resolved_document_id}_chunk_{chunk_index:03d}"

            payload = DocumentPayload(
                document_id=resolved_document_id,
                chunk_id=chunk_id,
                document_type=metadata.document_type,
                supplier=metadata.supplier,
                client=metadata.client,
                document_date=metadata.document_date,
                due_date=metadata.due_date,
                amount=metadata.amount,
                currency=metadata.currency,
                gst=metadata.gst,
                status=metadata.status,
                file_name=path.name,
                file_path=str(path),
                page=1,
                chunk_index=chunk_index,
                text=chunk_text,
            )

            chunk = DocumentChunk(
                point_id=str(uuid4()),
                text=chunk_text,
                payload=payload,
            )

            chunks.append(chunk)

        texts = [chunk.text for chunk in chunks]
        vectors = self.embedder.embed_texts(texts)

        self.store.upsert_chunks(
            chunks=chunks,
            vectors=vectors,
        )

        print("\nExtracted metadata:")
        print(metadata.model_dump(mode="json"))

        return IngestionResult(
            document_id=resolved_document_id,
            file_name=path.name,
            chunks_created=len(chunks),
            points_inserted=len(chunks),
            collection_name="accounting_documents",
        )