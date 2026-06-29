from app.file_ingestion import FileIngestionPipeline
from data.raw.sample_file import files

def main():
    pipeline = FileIngestionPipeline()

    for index, file_path in enumerate(files):
        print("\n" + "=" * 70)
        print(f"Ingesting: {file_path}")
        print("=" * 70)

        result = pipeline.ingest_file(
            file_path=file_path,
            recreate_collection=(index == 0),
        )

        print("Ingestion result:")
        print(result.model_dump(mode="json"))


if __name__ == "__main__":
    main()