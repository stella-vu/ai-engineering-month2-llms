from pathlib import Path

from app.document_classifier import DocumentClassifier
from app.document_parser import DocumentParser
from data.raw.sample_file import files

def main():
    parser = DocumentParser()
    classifier = DocumentClassifier()

    for file_path in files:
        print("\n" + "=" * 70)
        print(file_path)
        print("=" * 70)

        text = parser.parse_file(file_path)
        document_type = classifier.classify(text)

        print("Document type:", document_type)


if __name__ == "__main__":
    main()