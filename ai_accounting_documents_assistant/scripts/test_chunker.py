from pathlib import Path

from app.chunker import TextChunker
from app.document_parser import DocumentParser


def main():
    parser = DocumentParser()
    chunker = TextChunker()

    file_path = Path("data/raw/sample 1 - GBM-INV-2025-1001.pdf")

    text = parser.parse_file(file_path)
    chunks = chunker.split_text(text)

    print("File:", file_path)
    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print("\n" + "=" * 70)
        print(f"Chunk {index}")
        print("=" * 70)
        print(chunk)


if __name__ == "__main__":
    main()