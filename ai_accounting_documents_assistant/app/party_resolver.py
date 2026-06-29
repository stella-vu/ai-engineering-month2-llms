
class PartyResolver:
    """
    Resolves supplier and client from invoice/receipt text.

    Supplier = company issuing the document.
    Client = person/company under "Bill to".
    """

    def resolve_supplier(
        self,
        document_text: str,
        llm_supplier: str | None = None,
    ) -> str | None:
        lines = self._clean_lines(document_text)

        # Common pattern:
        # Invoice / Receipt
        # Invoice number ...
        # Date ...
        # Supplier company name
        for _, line in enumerate(lines):
            lower_line = line.lower()

            if lower_line.startswith(("invoice number", "receipt number", "date of issue", "date paid")):
                continue

            if self._looks_like_company_name(line):
                return line

        return llm_supplier

    def resolve_client(
        self,
        document_text: str,
        llm_client: str | None = None,
    ) -> str | None:
        lines = self._clean_lines(document_text)

        for index, line in enumerate(lines):
            if line.lower() == "bill to":
                if index + 1 < len(lines):
                    return lines[index + 1]

        return llm_client

    def _clean_lines(self, document_text: str) -> list[str]:
        return [
            line.strip()
            for line in document_text.splitlines()
            if line.strip()
        ]
    
    def _looks_like_company_name(self, line: str) -> bool:
        company_markers = [
            "inc",
            "ltd",
            "pty",
            "llc",
            "corp",
            "company",
            "consulting",
            "labs",
        ]

        lower_line = line.lower()

        if any(marker in lower_line for marker in company_markers):
            return True

        return False