import re


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    # Fix line-break hyphenation: safety-\nfocused -> safety-focused
    text = re.sub(r"(\w)-\n(\w)", r"\1-\2", text)
    # Join lines where PDF breaks normal sentences
    text = re.sub(r"(?<![\n.:])\n(?!\n)", " ", text)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+"," ", text)

    return text.strip()


def split_by_separator(text:str, separator: str) -> list[str]:
    if separator == "":
        return list(text)

    parts = text.split(separator)

    chunks = []

    for index, part in enumerate(parts):
        part = part.strip()

        if not part:
            continue

        if index < len(parts) - 1:
            chunks.append(part + separator)
        else:
            chunks.append(part)

    return chunks


def get_safe_overlap(text: str, chunk_overlap: int) -> str:
    if chunk_overlap <= 0:
        return ""

    overlap = text[-chunk_overlap:]

    # Move overlap start to the next safe boundary
    safe_boundaries = [". ", "\n", " "]

    for boundary in safe_boundaries:
        position = overlap.find(boundary)
        if position != -1:
            return overlap[position + len(boundary):].strip()

    return overlap.strip()



def merge_splits(
    splits: list[str],
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    chunks = []
    current_chunk = []
    current_length = 0

    for split in splits:
        split_length = len(split)

        if current_length + split_length > chunk_size and current_chunk:
            chunk = "".join(current_chunk).strip()

            if chunk:
                chunks.append(chunk)

            overlap_text = get_safe_overlap(chunk, chunk_overlap)

            current_chunk = []

            if overlap_text:
                current_chunk.append(overlap_text + " ")

            current_chunk.append(split)

            current_length = sum(len(part) for part in current_chunk)

        else:
            current_chunk.append(split)
            current_length += split_length

    final_chunk = "".join(current_chunk).strip()

    if final_chunk:
        chunks.append(final_chunk)

    return chunks


def recursive_split(
    text: str,
    separators: list[str],
    chunk_size: int,
) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    separator = separators[-1]

    for sep in separators:
        if sep == "" or sep in text:
            separator = sep
            break

    splits = split_by_separator(text, separator)

    final_splits = []

    next_separators = separators[separators.index(separator) + 1:]

    for split in splits:
        if len(split) <= chunk_size:
            final_splits.append(split)
        else:
            if next_separators:
                smaller_splits = recursive_split(
                    split,
                    next_separators,
                    chunk_size,
                )
                final_splits.extend(smaller_splits)
            else:
                final_splits.append(split)

    return final_splits


def chunk_text(
    text: str,
    chunk_size: int = 700,
    chunk_overlap: int = 120,
) -> list[str]:
    text = clean_text(text)

    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    separators = [
        "\n\n",
        "\n",
        ". ",
        "; ",
        ", ",
        " ",
    ]

    splits = recursive_split(
        text=text,
        separators=separators,
        chunk_size=chunk_size,
    )

    chunks = merge_splits(
        splits=splits,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return chunks