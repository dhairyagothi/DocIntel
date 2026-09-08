from models.document import Document, Page
from models.fact import Evidence, Fact
from models.relationship import Relationship
from validation.evidence_validator import validate_relationship


def test_invalid_page_gets_rejected():
    document = Document(document_id="d1", filename="a.pdf", file_hash="hash", page_count=1, pages=[Page(page_number=1, raw_text="Revenue was 100.", clean_text="Revenue was 100.")])
    fact = Fact(fact_id="a", subject="e", predicate="revenue", value=100, evidence=Evidence(document_id="d1", page=9, chunk_id="c", text="Revenue was 100."))
    other = Fact(fact_id="b", subject="e", predicate="revenue", value=100, evidence=Evidence(document_id="d1", page=1, chunk_id="c", text="Revenue was 100."))
    relationship = Relationship(relationship_id="r", fact_a="a", fact_b="b", classification="CORROBORATED", confidence=.9, reasoning="test", evidence_fact_a=fact.evidence.text, evidence_fact_b=other.evidence.text)
    validated = validate_relationship(relationship, {"a": fact, "b": other}, {"d1": document})
    assert validated.validation_errors