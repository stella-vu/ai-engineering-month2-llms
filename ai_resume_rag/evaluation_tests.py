from document_loader import load_text_file
from text_chunker import chunk_text
from vector_store import VectorStore
from rag_service import answer_question
from job_match_service import match_resume_to_job


def build_test_vector_store():
    file_path = "docs/Phuong Thao Vu (Stella) copy.pdf"

    resume_text = load_text_file(file_path)

    chunks = chunk_text(
        resume_text,
        chunk_size=700,
        chunk_overlap=120,
    )

    vector_store = VectorStore()

    vector_store.build_index(
        chunks=chunks,
        source=file_path,
    )

    return vector_store


def run_resume_qa_tests(vector_store):
    questions = [
        {
            "question": "What warehouse experience does this candidate have?",
            "expected": "Should mention warehouse operations, product accuracy, inventory discrepancies, damaged product reporting, or warehouse associate experience.",
        },
        {
            "question": "Does this candidate have inventory experience?",
            "expected": "Should mention inspecting and researching inventory discrepancies.",
        },
        {
            "question": "Does this candidate have picking experience?",
            "expected": "Should mention acting as a back-up product picker.",
        },
        {
            "question": "What education does this candidate have?",
            "expected": "Should mention B.S. Business Management and A.A. Business Administration.",
        },
        {
            "question": "Does this candidate have forklift experience?",
            "expected": "Should say forklift experience is not mentioned in the resume.",
        },
    ]

    print("\n" + "=" * 60)
    print("Resume Q&A Tests")
    print("=" * 60)

    for test in questions:
        result = answer_question(
            question=test["question"],
            vector_store=vector_store,
            top_k=4,
        )

        print("\nQuestion:")
        print(test["question"])

        print("\nExpected:")
        print(test["expected"])

        print("\nAnswer:")
        print(result["answer"])

        print("\nRetrieved chunks:")
        for chunk in result["retrieved_chunks"]:
            print(f"- Chunk {chunk['chunk_id']} | Score: {chunk['score']:.4f}")

        print("-" * 60)


def run_job_match_test(vector_store):
    job_description = """
    We are looking for a Warehouse Assistant responsible for picking, packing,
    inventory control, stock movement, dispatch preparation, manual handling,
    maintaining a clean and safe warehouse, and supporting daily warehouse operations.
    The ideal candidate should have good attention to detail, communication skills,
    a valid driver licence, and experience using warehouse systems or Excel.
    """

    result = match_resume_to_job(
        job_description=job_description,
        vector_store=vector_store,
        top_k=4,
    )

    print("\n" + "=" * 60)
    print("Job Match Test")
    print("=" * 60)

    if result["parse_error"]:
        print("Parse error:")
        print(result["parse_error"])
        print(result["raw_answer"])
        return

    answer = result["answer"]

    print(f"\nMatch Score: {answer.match_score}/100")

    print("\nMatched Skills:")
    for skill in answer.matched_skills:
        print(f"- {skill}")

    print("\nMissing or Weak Skills:")
    for skill in answer.missing_or_weak_skills:
        print(f"- {skill}")

    print("\nResume Improvement Suggestions:")
    for suggestion in answer.resume_improvement_suggestions:
        print(f"- {suggestion}")

    print("\nDo Not Add Unless True:")
    for item in answer.do_not_add_unless_true:
        print(f"- {item}")


def main():
    vector_store = build_test_vector_store()

    run_resume_qa_tests(vector_store)
    run_job_match_test(vector_store)


if __name__ == "__main__":
    main()