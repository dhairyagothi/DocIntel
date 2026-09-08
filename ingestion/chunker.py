import re

from config import MAX_CHUNK_CHARS
from models.document import Chunk, Document


def create_chunks(document: Document, max_chars: int = MAX_CHUNK_CHARS) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page in document.pages:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n|(?<=[.!?])\s{2,}", page.clean_text) if part.strip()]
        if not paragraphs and page.clean_text:
            paragraphs = [page.clean_text]
        current = ""
        index = 1
        for paragraph in paragraphs:
            if current and len(current) + len(paragraph) + 2 > max_chars:
                chunks.append(Chunk(
                    chunk_id=f"{document.document_id}-P{page.page_number}-C{index:02d}",
                    document_id=document.document_id,
                    page_start=page.page_number,
                    page_end=page.page_number,
                    text=current.strip(),
                ))
                index += 1
                current = ""
            current = f"{current}\n\n{paragraph}".strip()
        if current:
            chunks.append(Chunk(
                chunk_id=f"{document.document_id}-P{page.page_number}-C{index:02d}",
                document_id=document.document_id,
                page_start=page.page_number,
                page_end=page.page_number,
                text=current.strip(),
            ))
    return chunks