import tempfile
from pathlib import Path

import streamlit as st

from document_loader import load_text_file
from text_chunker import chunk_text
from vector_store import VectorStore
from rag_service import answer_question
from job_match_service import match_resume_to_job
from tailoring_service import generate_tailored_resume_suggestions


st.set_page_config(
    page_title="AI Resume RAG Assistant",
    page_icon="📄",
    layout="wide",
)


def save_uploaded_file(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def build_vector_store(file_path: str, source_name: str) -> tuple[VectorStore, list[str]]:
    resume_text = load_text_file(file_path)

    chunks = chunk_text(
        resume_text,
        chunk_size=700,
        chunk_overlap=120,
    )

    vector_store = VectorStore()

    vector_store.build_index(
        chunks=chunks,
        source=source_name,
    )

    return vector_store, chunks


def main():
    st.title("AI Resume RAG Assistant")
    st.caption(
        "Ask questions about an uploaded resume using local embeddings, FAISS, and Ollama."
    )

    uploaded_file = st.file_uploader(
        "Upload a resume",
        type=["pdf", "docx", "txt"],
    )

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

    if "chunks" not in st.session_state:
        st.session_state.chunks = []

    if "source_name" not in st.session_state:
        st.session_state.source_name = None

    if uploaded_file is not None:
        st.info(f"Uploaded: {uploaded_file.name}")

        if st.button("Build Resume Index"):
            with st.spinner("Reading resume, creating chunks, and building FAISS index..."):
                file_path = save_uploaded_file(uploaded_file)

                vector_store, chunks = build_vector_store(
                    file_path=file_path,
                    source_name=uploaded_file.name,
                )

                st.session_state.vector_store = vector_store
                st.session_state.chunks = chunks
                st.session_state.source_name = uploaded_file.name

            st.success(
                f"Index built successfully. Total chunks: {len(st.session_state.chunks)}"
            )

    if st.session_state.vector_store is not None:

        tab_qa, tab_match, tab_tailor, tab_chunks = st.tabs(
            [
                "Resume Q&A",
                "Job Match",
                "Tailored Suggestions",
                "Resume Chunks",
            ]
        )

        with tab_qa:
            st.subheader("Ask a question about the resume")

            question = st.text_input(
                "Question",
                placeholder="Example: What warehouse and inventory experience does this candidate have?",
            )

            col1, _ = st.columns([1, 4])

            with col1:
                top_k = st.number_input(
                    "Top K",
                    min_value=1,
                    max_value=6,
                    value=4,
                    step=1,
                    key="qa_top_k"
                )

            if st.button("Ask", key="ask_question"):
                if not question.strip():
                    st.warning("Please enter a question.")
                else:
                    with st.spinner("Retrieving relevant chunks and generating answer..."):
                        result = answer_question(
                            question=question,
                            vector_store=st.session_state.vector_store,
                            top_k=top_k,
                        )

                    st.subheader("Answer")
                    st.write(result["answer"])

                    st.subheader("Retrieved Evidence")

                    for chunk in result["retrieved_chunks"]:
                        with st.expander(
                            f"Chunk {chunk['chunk_id']} | Score: {chunk['score']:.4f}"
                        ):
                            st.caption(f"Source: {chunk['source']}")
                            st.write(chunk["text"])

        with tab_match:
            st.subheader("Match resume to job description")

            job_description = st.text_area(
                "Paste job description",
                height=220,
                placeholder="Paste the job description here...",
                key="match_job_description",
            )

            if st.button("Match Resume to Job", key="match_resume"):
                if not job_description.strip():
                    st.warning("Please paste a job description.")
                else:
                    with st.spinner("Comparing resume against job description..."):
                        match_result = match_resume_to_job(
                            job_description=job_description,
                            vector_store=st.session_state.vector_store,
                            top_k=4,
                        )

                    st.subheader("Job Match Result")

                    if match_result["parse_error"]:
                        st.error("The model did not return valid structured output.")
                        st.write(match_result["parse_error"])
                        st.text(match_result["raw_answer"])
                    else:
                        answer = match_result["answer"]

                        st.metric("Match Score", f"{answer.match_score}/100")

                        st.markdown("#### Matched Skills")
                        for skill in answer.matched_skills:
                            st.write(f"- {skill}")

                        st.markdown("#### Missing or Weak Skills")
                        for skill in answer.missing_or_weak_skills:
                            st.write(f"- {skill}")

                        st.markdown("#### Resume Improvement Suggestions")
                        for suggestion in answer.resume_improvement_suggestions:
                            st.write(f"- {suggestion}")

                        st.markdown("#### Do Not Add Unless True")
                        for item in answer.do_not_add_unless_true:
                            st.write(f"- {item}")

                    st.subheader("Retrieved Resume Evidence")

                    for chunk in match_result["retrieved_chunks"]:
                        with st.expander(
                            f"Chunk {chunk['chunk_id']} | Score: {chunk['score']:.4f}"
                        ):
                            st.caption(f"Source: {chunk['source']}")
                            st.write(chunk["text"])
        
        with tab_tailor:
            st.subheader("Generate tailored resume suggestions")

            tailoring_job_description = st.text_area(
                "Paste job description for tailoring",
                height=220,
                placeholder="Paste the job description here...",
                key="tailoring_job_description",
            )

            if st.button("Generate Tailored Suggestions", key="generate_tailoring"):
                if not tailoring_job_description.strip():
                    st.warning("Please paste a job description.")
                else:
                    with st.spinner("Generating truthful resume suggestions..."):
                        tailoring_result = generate_tailored_resume_suggestions(
                            job_description=tailoring_job_description,
                            vector_store=st.session_state.vector_store,
                            top_k=4,
                        )

                    st.subheader("Tailored Resume Suggestions")
                    st.write(tailoring_result["answer"])

                    st.subheader("Retrieved Resume Evidence")

                    for chunk in tailoring_result["retrieved_chunks"]:
                        with st.expander(
                            f"Chunk {chunk['chunk_id']} | Score: {chunk['score']:.4f}"
                        ):
                            st.caption(f"Source: {chunk['source']}")
                            st.write(chunk["text"])

        with tab_chunks:
            st.subheader("Resume chunks")

            st.caption(
                "These are the chunks created from the uploaded resume before embedding and FAISS indexing."
            )

            st.write(f"Total chunks: {len(st.session_state.chunks)}")

            for index, chunk in enumerate(st.session_state.chunks):
                with st.expander(f"Chunk {index}"):
                    st.write(chunk)


if __name__ == "__main__":
    main()