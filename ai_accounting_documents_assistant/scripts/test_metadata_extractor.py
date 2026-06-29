from app.document_parser import DocumentParser
from app.metadata_extractor import MetadataExtractor
from data.raw.sample_file import files


def main():

    for file_path in files:
        parser = DocumentParser()
        extractor = MetadataExtractor()

        text = parser.parse_file(file_path)
        metadata = extractor.extract(text)

        print("Extracted metadata:")
        print(metadata.model_dump(mode="json"))


if __name__ == "__main__":
    main()