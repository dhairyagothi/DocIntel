from typing import Any

from pydantic import BaseModel, Field


class Page(BaseModel):
    page_number: int
    width: float = 0
    height: float = 0
    raw_text: str = ""
    clean_text: str = ""
    blocks: list[dict[str, Any]] = Field(default_factory=list)


class Document(BaseModel):
    document_id: str
    filename: str
    file_hash: str
    page_count: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    pages: list[Page] = Field(default_factory=list)


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    page_start: int
    page_end: int
    text: str