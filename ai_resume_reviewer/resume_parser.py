import re
from pypdf import PdfReader

def fix_spaced_characters(text: str) -> str:
    # Fix text like: A b o u t  m e -> About me
    if len(text.split()) > 10:
        single_char_words = sum(1 for word in text.split() if len(word) == 1)
        total_words = len(text.split())

        if single_char_words / total_words > 0.9:
            text = text.replace(" ", "")

            # Add spaces before capital letters where words likely start
            text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)

    return text


def clean_extracted_text(text: str) -> str:
    text = fix_spaced_characters(text)

    # Join words/sentences broken by PDF line wrapping
    text = re.sub(r"(?<![.!?:])\n(?!\n)", " ", text)

    # Remove too many spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Keep paragraph breaks clean
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
    
    return clean_extracted_text(text)

# file = "/Users/stellavu/ai-engineering-month2/ai_resume_reviewer/Warehouse - Phuong Thao Vu (Stella) copy.pdf"
# print(extract_text_from_pdf(file))
