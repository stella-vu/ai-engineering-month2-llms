from document_loader import load_text_file
from text_chunker import chunk_text


def main():
    file_path = "docs/sample_warehouse_resume.docx"

    resume_text = load_text_file(file_path)

    chunks = chunk_text(
        resume_text,
        chunk_size=700,
        chunk_overlap=120,
    )

    print(f"\nLoaded file: {file_path}")
    print(f"Total characters: {len(resume_text)}")
    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print("\n" + "-" * 60)
        print(f"Chunk {index}")
        print("-" * 60)
        print(chunk)


if __name__ == "__main__":
    main()