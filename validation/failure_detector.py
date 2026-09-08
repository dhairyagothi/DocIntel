import re
from collections import Counter

from models.document import Document
from models.fact import Fact


def detect_failures(facts: list[Fact], documents: list[Document]) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    pages = {document.document_id: document.page_count for document in documents}
    for fact in facts:
        if fact.evidence.page > pages.get(fact.evidence.document_id, 0):
            failures.append({"severity": "high", "type": "INVALID_PAGE", "message": f"{fact.fact_id} references a page outside the source document."})
        if not fact.evidence.text.strip():
            failures.append({"severity": "high", "type": "EMPTY_EVIDENCE", "message": f"{fact.fact_id} has no evidence anchor."})
        if fact.unit == "%" and fact.predicate not in {"growth", "market_share", "margin", "percentage"}:
            failures.append({"severity": "medium", "type": "PERCENT_AS_AMOUNT", "message": f"{fact.fact_id} may have treated a percentage as a primary amount."})
    duplicate_keys = Counter((fact.evidence.document_id, fact.subject, fact.predicate, str(fact.normalized_value), fact.time_period) for fact in facts)
    for key, count in duplicate_keys.items():
        if count > 1:
            failures.append({"severity": "low", "type": "DUPLICATE_FACT", "message": f"Duplicate candidate facts detected within {key[0]} for {key[2]} ({count} occurrences)."})
    return failures