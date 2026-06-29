from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class DocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    CONTRACT = "contract"
    OTHER = "other"


class PaymentStatus(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    OVERDUE = "overdue"
    PARTIAL = "partial"
    NOT_APPLICABLE = "n/a"
    UNKNOWN = "unknown"


class Currency(str, Enum):
    AUD = "AUD"
    USD = "USD"
    VND = "VND"
    OTHER = "OTHER"


class ExtractedMetadata(BaseModel):
    document_type: DocumentType = DocumentType.OTHER
    supplier: str | None = None
    client: str | None = None
    document_date: date | None = None
    due_date: date | None = None
    amount: float | None = Field(default=None, ge=0)
    currency: Currency = Currency.OTHER
    gst: float | None = Field(default=None, ge=0)
    status: PaymentStatus = PaymentStatus.UNKNOWN
    model_config = ConfigDict(use_enum_values=True)

class DocumentPayload(BaseModel):
    """
    Metadata stored inside each Qdrant point payload.

    Vector = semantic meaning
    Payload = business facts
    """

    document_id: str = Field(
        ...,
        description="Unique ID for the original document.",
        examples=["doc_001_chunk_000"],
    )

    chunk_id: str = Field(
        ...,
        description="Human-readable chunk ID within the original document.",
        examples=["doc_001_chunk_000"],
    )

    document_type: DocumentType = Field(
        ...,
        description="Business type of the document.",
        examples=[DocumentType.INVOICE],
    )

    supplier: str | None = Field(
        default=None,
        description="Supplier, vendor, bank, or document issuer.",
        examples=["Officeworks"],
    )

    client: str | None = Field(
        default=None,
        description="Client or business owner related to this document.",
        examples=["Client A"],
    )

    document_date: date | None = Field(
        default=None,
        description="Main date of the document, such as invoice date, receipt date, or statement date.",
        examples=["2026-06-12"],
    )

    due_date: date | None = Field(
        default=None,
        description="Payment due date, mainly useful for invoices.",
        examples=["2026-07-12"],
    )

    amount: float | None = Field(
        default=None,
        ge=0,
        description="Total amount on the document.",
        examples=[650.00],
    )

    currency: Currency = Field(
        default=Currency.AUD,
        description="Currency of the document amount.",
    )

    gst: float | None = Field(
        default=None,
        ge=0,
        description="GST or tax amount if available.",
        examples=[59.09],
    )

    status: PaymentStatus = Field(
        default=PaymentStatus.UNKNOWN,
        description="Payment status or document status.",
    )

    file_name: str = Field(
        ...,
        description="Original uploaded file name.",
        examples=["officeworks_invoice_june.pdf"],
    )

    file_path: str | None = Field(
        default=None,
        description="Local or stored path to the source file.",
        examples=["data/raw/officeworks_invoice_june.pdf"],
    )

    page: int | None = Field(
        default=None,
        ge=1,
        description="Page number where the chunk came from.",
        examples=[1],
    )

    chunk_index: int = Field(
        ...,
        ge=0,
        description="Chunk number within the document.",
        examples=[0],
    )

    text: str = Field(
        ...,
        min_length=1,
        description="Original text content of this chunk.",
    )

    model_config = ConfigDict(use_enum_values=True)


class DocumentChunk(BaseModel):
    """
    One text chunk before insertion into Qdrant.
    """

    point_id: str = Field(
        ...,
        description="Unique Qdrant point ID for this chunk.",
        examples=["doc_001_chunk_000"],
    )

    text: str = Field(
        ...,
        min_length=1,
        description="Chunk text to embed and store.",
    )

    payload: DocumentPayload = Field(
        ...,
        description="Metadata payload stored with the chunk.",
    )


class SearchFilters(BaseModel):
    """
    Optional filters used during Qdrant retrieval.
    """

    document_type: DocumentType | None = None
    supplier: str | None = None
    client: str | None = None
    status: PaymentStatus | None = None
    min_gst: float | None = Field(
        default=None,
        ge=0,
        description="Only return documents with GST greater than or equal to this amount.",
    )

    max_gst: float | None = Field(
        default=None,
        ge=0,
        description="Only return documents with GST less than or equal to this amount.",
    )

    start_date: date | None = Field(
        default=None,
        description="Only return documents on or after this date.",
    )

    end_date: date | None = Field(
        default=None,
        description="Only return documents on or before this date.",
    )

    min_amount: float | None = Field(
        default=None,
        ge=0,
        description="Only return documents with amount greater than or equal to this value.",
    )

    max_amount: float | None = Field(
        default=None,
        ge=0,
        description="Only return documents with amount less than or equal to this value.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of search results to return.",
    )

    model_config = ConfigDict(use_enum_values=True)


class SearchResult(BaseModel):
    """
    One result returned from Qdrant search.
    """

    point_id: str
    score: float
    payload: DocumentPayload
    text: str


class IngestionResult(BaseModel):
    """
    Summary after ingesting one or more documents.
    """

    document_id: str
    file_name: str
    chunks_created: int
    points_inserted: int
    collection_name: str


class RetrievedContext(BaseModel):
    """
    Context passed into the LLM after retrieval.
    """

    query: str
    filters: SearchFilters | None = None
    results: list[SearchResult]


class AIAnswer(BaseModel):
    """
    Final structured answer from the assistant.
    """

    answer: str
    sources: list[SearchResult]
    confidence: str = Field(
        ...,
        description="Simple confidence label: low, medium, or high.",
        examples=["high"],
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Any information the retrieved documents did not contain.",
    )


