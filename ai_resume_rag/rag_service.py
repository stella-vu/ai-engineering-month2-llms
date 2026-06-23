from ollama_client import chat_with_ollama
from vector_store import VectorStore


def format_context(retrieved_chunks: list[dict]) -> str:
    context_parts = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f"""
[Context {index}]
Source: {chunk["source"]}
Chunk ID: {chunk["chunk_id"]}
Text:
{chunk["text"]}
"""
        )

    return "\n".join(context_parts)


def answer_question(
    question: str,
    vector_store: VectorStore,
    top_k: int = 4,
) -> dict:
    retrieved_chunks = vector_store.search(
        query=question,
        top_k=top_k,
    )

    context = format_context(retrieved_chunks)

    prompt = f"""
You are a resume question-answering assistant.

Answer the user's question using ONLY the context below.

Rules:
- Do not invent information.
- If the context does not contain the answer, say: "I don't know based on the uploaded resume."
- Be specific and concise.
- Mention the evidence from the resume when useful.

Context:
{context}

Question:
{question}

Answer:
"""

    answer = chat_with_ollama(prompt)

    return {
        "answer": answer,
        "retrieved_chunks": retrieved_chunks,
    }