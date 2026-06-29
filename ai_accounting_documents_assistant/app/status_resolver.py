from app.schemas import DocumentType, PaymentStatus


class StatusResolver:
    """
    Resolves payment status from document text using accounting evidence.
    """

    def resolve(
        self,
        document_text: str,
        document_type: DocumentType | str
    ) -> PaymentStatus:
        text = document_text.lower()

        paid_markers = [
            "date paid",
            "amount paid",
            "paid on",
            "paid by",
            "payment received",
            "paid successfully",
            "paid in full",
            "receipt number",
            "payment history",
        ]

        unpaid_markers = [
            "amount due",
            "due date",
            "date due",
            "pay online",
            "payment instructions",
            "remittance",
        ]

        has_paid_marker = any(marker in text for marker in paid_markers)
        has_unpaid_marker = any(marker in text for marker in unpaid_markers)

        normalized_type = (
            document_type.value if hasattr(document_type, "value") else document_type
        )

        if has_paid_marker:
            return PaymentStatus.PAID

        if normalized_type == "invoice" and has_unpaid_marker:
            return PaymentStatus.UNPAID

        if normalized_type == "receipt":
            return PaymentStatus.PAID

        return PaymentStatus.UNKNOWN