from ollama_client import chat_with_ollama
from vector_store import VectorStore
from rag_service import format_context


def generate_tailored_resume_suggestions(
    job_description: str,
    vector_store: VectorStore,
    top_k: int = 4,
) -> dict:
    retrieved_chunks = vector_store.search(
        query=job_description,
        top_k=top_k,
    )

    context = format_context(retrieved_chunks)

    prompt = f"""
You are a professional resume improvement assistant.

Your task is to suggest how to tailor the resume for the job description.

Use ONLY the resume context below.
Do NOT invent skills, tools, licences, certifications, achievements, or work experience.

Business rules:
- Only suggest improvements supported by the resume context.
- If the job requires something not found in the resume, clearly mark it as a gap.
- Do not write fake resume bullet points.
- Suggested bullet points must be truthful and based on existing experience.
- Keep the language professional and suitable for an Australian resume.
- If the job description requires or prefers a skill that is not clearly supported by the resume context, you MUST list it under "Gaps to be honest about".
- "Gaps to be honest about" must not say "None" if there are any items listed under "Do not add unless true".
- "Do not add unless true" should repeat unsupported job requirements that the candidate may have but the resume does not prove.
-Before writing each suggested bullet point, verify that every skill, tool, system, licence, or achievement in the bullet is\ 
explicitly supported by the resume context. If not supported, do not include it in the suggested bullet.
Return your answer in this format:

#### Suggested professional summary:
...

#### Suggested skills to highlight:
- ...

#### Suggested resume bullet improvements:
1. Focus:
- Resume evidence used:
- Suggested bullet:
- Why this is safe to use:

#### Gaps to be honest about:
- Required/preferred skill from job:
  Resume evidence status:
  Honest advice:

#### Do not add unless true:
- ...

Resume context:
{context}

Job description:
{job_description}

Answer:
"""

    answer = chat_with_ollama(prompt)

    return {
        "answer": answer,
        "retrieved_chunks": retrieved_chunks,
    }