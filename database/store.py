from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Iterable

from config import DATABASE_PATH
from models.document import Chunk, Document
from models.fact import Fact
from models.relationship import Relationship


def init_db() -> None:
    schema = (DATABASE_PATH.parent / "schema.sql").read_text()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(schema)


def persist(documents: Iterable[Document], chunks: Iterable[Chunk], facts: Iterable[Fact], relationships: Iterable[Relationship]) -> None:
    init_db()
    with sqlite3.connect(DATABASE_PATH) as connection:
        for document in documents:
            connection.execute(
                "INSERT OR REPLACE INTO documents VALUES (?, ?, ?, ?, ?)",
                (document.document_id, document.filename, document.file_hash, document.page_count, datetime.now(timezone.utc).isoformat()),
            )
        for chunk in chunks:
            connection.execute("INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?)", (chunk.chunk_id, chunk.document_id, chunk.page_start, chunk.page_end, chunk.text))
        for fact in facts:
            connection.execute(
                "INSERT OR REPLACE INTO facts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (fact.fact_id, fact.subject, fact.predicate, json.dumps(fact.value, default=str), json.dumps(fact.normalized_value, default=str),
                 fact.unit, fact.currency, fact.time_period, fact.scope, fact.confidence, fact.evidence.document_id,
                 fact.evidence.page, fact.evidence.chunk_id, fact.evidence.text),
            )
        for relationship in relationships:
            connection.execute(
                "INSERT OR REPLACE INTO relationships VALUES (?, ?, ?, ?, ?, ?, ?)",
                (relationship.relationship_id, relationship.fact_a, relationship.fact_b, relationship.classification,
                 relationship.confidence, json.dumps(relationship.reason_codes), relationship.reasoning),
            )
        connection.commit()