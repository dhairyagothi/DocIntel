from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

import pymupdf as fitz

from models.document import Document, Page
from utils.hashing import document_hash, stable_id


def extract_pdf(source: str | Path | bytes | BinaryIO, filename: str | None = None) -> Document:
    if isinstance(source, (str, Path)):
        path = Path(source)
        payload = path.read_bytes()
        filename = filename or path.name
    elif isinstance(source, bytes):
        payload = source
        filename = filename or "uploaded.pdf"
    else:
        payload = source.read()
        filename = filename or getattr(source, "name", "uploaded.pdf")

    file_hash = document_hash(payload)
    document_id = stable_id("DOC", file_hash)
    pdf = fitz.open(stream=payload, filetype="pdf")
    pages: list[Page] = []
    metadata = dict(pdf.metadata or {})
    for number, page in enumerate(pdf, start=1):
        blocks = []
        for block in page.get_text("blocks"):
            if len(block) >= 5 and str(block[4]).strip():
                blocks.append({"x0": block[0], "y0": block[1], "x1": block[2], "y1": block[3], "text": block[4]})
        pages.append(Page(
            page_number=number,
            width=page.rect.width,
            height=page.rect.height,
            raw_text=page.get_text("text"),
            blocks=blocks,
        ))
    pdf.close()
    return Document(
        document_id=document_id,
        filename=filename,
        file_hash=file_hash,
        page_count=len(pages),
        metadata=metadata,
        pages=pages,
    )