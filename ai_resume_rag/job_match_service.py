import json
from ollama_client import chat_with_ollama
from vector_store import VectorStore
from rag_service import format_context
from schemas import JobMatchResult

def match_resume_to_job(
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
You are a resume-job matching assistant.

Compare the uploaded resume context against the job description.

Use ONLY the resume context below.
Do NOT invent experience, tools, licences, certifications, achievements, or results.

Business rules:
- If a skill is clearly supported by the resume, include it in matched_skills.
- If a job requirement is missing or weak in the resume context, include it in missing_or_weak_skills.
- Unsupported job requirements must be included in do_not_add_unless_true.
- Suggestions must be truthful and based only on the candidate's real experience.
- resume_improvement_suggestions must contain 2 to 4 truthful, practical suggestions.
- Do not suggest adding fake skills.
- Return only valid JSON.
- Do not include markdown.
- Do not include explanation outside JSON.

Scoring rules:
- 90-100: Strong match. Most key requirements are clearly supported by the resume.
- 75-89: Good match. Many key requirements are supported, with a few gaps.
- 60-74: Partial match. Some relevant experience, but several important gaps.
- 40-59: Weak match. Limited relevant experience.
- 1-39: Very weak match. Almost no relevant experience.
- 0: No relevant matched skills at all.
- If matched_skills is not empty, match_score must be greater than 0.
- If matched_skills contains 5 or more relevant skills, match_score should usually be at least 60.

JSON format example only:
{{
  "match_score": 75,
  "matched_skills": ["example supported skill"],
  "missing_or_weak_skills": ["example missing or weak skill"],
  "resume_improvement_suggestions": ["example truthful suggestion"],
  "do_not_add_unless_true": ["example unsupported requirement"]
}}

Resume context:
{context}

Job description:
{job_description}

Answer:
"""

    raw_answer = chat_with_ollama(prompt)

    try:
        parsed_json = json.loads(raw_answer)
        validate_result = JobMatchResult(**parsed_json)

        return {
            "answer": validate_result,
            "raw_answer": raw_answer,
            "retrieved_chunks": retrieved_chunks,
            "parse_error": None,
        }

    except Exception as e:
        return {
            "answer": None,
            "raw_answer": raw_answer,
            "retrieved_chunks": retrieved_chunks,
            "parse_error": str(e),
        }