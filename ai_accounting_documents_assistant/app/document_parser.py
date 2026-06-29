from pathlib import Path

import fitz


SUPPORTED_EXTENSIONS = {".txt", ".pdf"}


class DocumentParser:
    """
    Simple document parser for readable text files and readable PDFs.

    This does not handle scanned PDFs yet.
    Scanned PDFs need OCR.
    """

    def parse_file(self, file_path: str | Path) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. "
                f"Supported types: {SUPPORTED_EXTENSIONS}"
            )

        if path.suffix.lower() == ".txt":
            return self._parse_txt(path)

        if path.suffix.lower() == ".pdf":
            return self._parse_pdf(path)

        raise ValueError(f"Unsupported file type: {path.suffix}")

    def _parse_txt(self, path: Path) -> str:
        text = path.read_text(encoding="utf-8")
        return self._clean_text(text)

    def _parse_pdf(self, path: Path) -> str:
        document = fitz.open(path)

        pages_text = []

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text")
            cleaned_page_text = self._clean_text(page_text)

            if cleaned_page_text:
                pages_text.append(
                    f"\n--- Page {page_number} ---\n{cleaned_page_text}"
                )

        document.close()

        full_text = "\n".join(pages_text)

        if not full_text.strip():
            raise ValueError(
                "No readable text found. This may be a scanned PDF and may need OCR."
            )

        return full_text

    def _clean_text(self, text: str) -> str:
        lines = []

        for line in text.splitlines():
            cleaned_line = " ".join(line.split())

            if cleaned_line:
                lines.append(cleaned_line)

        return "\n".join(lines)