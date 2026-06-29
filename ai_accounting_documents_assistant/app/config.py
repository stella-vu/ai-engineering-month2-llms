COLLECTION_NAME = "accounting_documents"

QDRANT_URL = "http://localhost:6333"

EMBEDDING_MODEL = "nomic-embed-text"

LLM_MODEL = "llama3.2:latest"

# nomic-embed-text through Ollama commonly returns 768-dimensional vectors.
VECTOR_SIZE = 768

DISTANCE_METRIC = "Cosine"