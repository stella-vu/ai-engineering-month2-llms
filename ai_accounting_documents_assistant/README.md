# AI Accounting Document Assistant v1

A local RAG-based accounting document assistant built with **Qdrant**, **Ollama**, **LangChain text splitters**, **Pydantic**, and a local LLM.  
The app can ingest readable PDF accounting documents, extract and validate metadata, store document chunks in a vector database, and answer user questions with source-backed responses.

## Project Goal

This project was built to practice a more realistic AI engineering workflow for document search and accounting assistance. Instead of only storing text in a vector database, the app combines semantic search with structured business metadata such as document type, supplier, client, amount, GST, date, due date, and payment status.

## Pipeline

```text
PDF documents
→ DocumentParser
→ DocumentClassifier
→ MetadataExtractor
→ Validation resolvers
→ LangChain TextChunker
→ Ollama embeddings
→ Qdrant vector database
→ DocumentRetriever
→ RAGAssistant
→ Answer with sources
```

## What Makes This Better Than the Original Pipeline

The original pipeline was simple:

```
sample text
→ fake/manual embeddings
→ Qdrant
→ basic search
```

The upgraded pipeline is closer to a practical document assistant:
 
- Uses **real embeddings** with `nomic-embed-text` instead of fake vectors.
- Uses **Qdrant payload metadata** for business filters.
- Parses **real readable PDFs** instead of only sample text.
- Uses `LangChain RecursiveCharacterTextSplitter` for better chunking.
- Adds document classification before extraction.
- Uses a **local LLM** for metadata extraction, but does not fully trust it.
- Adds **deterministic resolvers** for currency, status, tax/GST, and parties.
- Supports multi-file ingestion.
- Retrieves using both **semantic meaning** and **metadata filters**.
- Generates grounded answers through a `RAGAssistant`.
- Shows source file names and chunk IDs for transparency.

## Current Features

- Ingest multiple invoice and receipt PDFs.
- Extract metadata with Pydantic validation.
- Store chunks and payloads in Qdrant.
- Search by document type, supplier, status, amount, date, and GST.
- Ask accounting-style questions such as:
    - “Which invoices are unpaid?”
    - “What documents do I have from Eleven Labs?”
    - “Which documents include Australian GST?”

## Limitations

This version only supports readable PDFs. Scanned PDFs and photos need OCR. Metadata extraction can still be imperfect because local LLMs may return inconsistent results.

## Next Version Improvements

- Add Azure AI Document Intelligence for OCR and scanned PDFs.
- Extract invoice numbers and receipt numbers.
- Link invoices and receipts for payment reconciliation.
- Add confidence scores and `needs_review` flags.
- Store structured metadata in PostgreSQL.
- Add a Streamlit or FastAPI interface.
- Improve duplicate detection before ingestion.