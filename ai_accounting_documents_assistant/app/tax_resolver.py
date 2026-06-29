import re


class TaxResolver:
    """
    Resolves GST/tax amount from document text.

    For Australian GST shown with AUD equivalent, prefer the A$ value.
    Example:
    GST - Australia (10% on $11.00)
    $1.10
    (A$1.53)
    """

    def resolve_gst(self, document_text: str, llm_gst: float | None = None) -> float | None:
        text = document_text

        aud_gst_match = re.search(
            r"GST\s*-\s*Australia[\s\S]{0,120}A\$(\d+(?:\.\d{1,2})?)",
            text,
            flags=re.IGNORECASE,
        )

        if aud_gst_match:
            return float(aud_gst_match.group(1))

        gst_match = re.search(
            r"GST[\s\S]{0,80}\$(\d+(?:\.\d{1,2})?)",
            text,
            flags=re.IGNORECASE,
        )

        if gst_match:
            return float(gst_match.group(1))

        return llm_gst