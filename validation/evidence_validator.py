from models.document import Document
from models.fact import Fact
from models.relationship import Relationship


def validate_relationship(relationship: Relationship, facts_by_id: dict[str, Fact], documents_by_id: dict[str, Document]) -> Relationship:
    errors = []
    for fact_id in (relationship.fact_a, relationship.fact_b):
        fact = facts_by_id.get(fact_id)
        if not fact:
            errors.append(f"Missing fact: {fact_id}")
            continue
        if fact.evidence.document_id not in documents_by_id:
            errors.append(f"Missing document: {fact.evidence.document_id}")
            continue
        document = documents_by_id[fact.evidence.document_id]
        if not 1 <= fact.evidence.page <= document.page_count:
            errors.append(f"Invalid page {fact.evidence.page} for {document.filename}")
            continue
        if not fact.evidence.text.strip():
            errors.append(f"Empty evidence for {fact_id}")
        chunk = next((page.clean_text for page in document.pages if page.page_number == fact.evidence.page), "")
        if fact.evidence.text.lower() not in chunk.lower() and fact.evidence.text.lower() not in document.pages[fact.evidence.page - 1].raw_text.lower():
            errors.append(f"Evidence text not found on source page for {fact_id}")
    relationship.validation_errors = errors
    return relationship