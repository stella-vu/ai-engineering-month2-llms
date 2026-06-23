# AI Resume RAG Assistant

A local AI-powered Resume RAG Assistant built with Streamlit, Ollama, FAISS, and Python.

This app allows users to upload a resume, ask questions about the resume, compare it against a job description, and generate truthful resume improvement suggestions using retrieved document evidence.

## Project Overview

This project demonstrates a full local Retrieval-Augmented Generation pipeline:

```text
Resume document
→ Text extraction
→ Recursive chunking
→ Embeddings with Ollama
→ FAISS vector search
→ Retrieved context
→ Local LLM answer
```

## Features

### 1. Resume Q&A

Upload a resume and ask questions such as:

``` 
What warehouse experience does this candidate have?
Does this candidate have inventory experience?
What education does this candidate have?
Does this candidate have forklift experience?
```

The app retrieves relevant resume chunks and answers using only the retrieved context.

### 2. Resume-to-Job Matching

Paste a job description and receive a structured match result:

- Match score
- Matched skills
- Missing or weak skills
- Resume improvement suggestions
- Skills not to add unless true

The match result uses **Pydantic validation** to reduce inconsistent model outputs.

### 3. Tailored Resume Suggestions

Generate truthful resume improvement suggestions based on the job description.

The app is designed to avoid fake resume claims. Unsupported skills, tools, licences, or certifications are marked as gaps instead of being added to the resume.

### 4. Retrieved Evidence Display

Each AI answer shows the retrieved chunks used as evidence, including:

- Chunk ID
- Similarity score
- Source document
- Retrieved text

This makes the app more transparent and easier to debug.

### 5. Evaluation Tests

The project includes manual evaluation tests to check:

- Relevant questions retrieve relevant chunks
- Unsupported skills are not invented
- Job match scores are consistent with matched skills
- Missing skills are correctly identified

## Future Improvements

### Current limitations:

- FAISS index is stored in memory only.
- The app currently indexes one uploaded resume at a time.
- PDF extraction quality depends on resume layout.
- The LLM may still need prompt tuning for stricter output quality.
- There is no user authentication or persistent database.
- The app does not edit the actual resume file.

### Possible upgrades:

- Add Qdrant for persistent vector database storage
- Add multi-resume comparison
- Add exportable job match reports
- Add structured output for tailored suggestions
- Add source citations inside answers
- Add resume red-flag detection
- Add FastAPI backend
- Add PostgreSQL or SQLite for history tracking
- Add a cleaned sample dataset for testing
- Add automated RAG evaluation