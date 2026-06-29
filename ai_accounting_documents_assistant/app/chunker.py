from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """
    Production-style text chunker using LangChain's RecursiveCharacterTextSplitter.

    Keeps our app interface simple:
    text -> list[str]
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    def split_text(self, text: str) -> list[str]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        return self.splitter.split_text(text)