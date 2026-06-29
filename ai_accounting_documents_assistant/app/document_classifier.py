class DocumentClassifier:
    """
    Classify documents to receipt, invoice, bank statement, contract\
    and other to review.
    To route each document to the correct extractor
    """
    def classify(self, text: str) -> str:
        text_lower = text.lower()

        if "receipt number" in text_lower or "date paid" in text_lower:
            return "receipt"

        if "invoice" in text_lower or "amount due" in text_lower:
            return "invoice"

        if "opening balance" in text_lower and "closing balance" in text_lower:
            return "bank_statement"

        if "agreement" in text_lower or "contract" in text_lower:
            return "contract"

        return "other"