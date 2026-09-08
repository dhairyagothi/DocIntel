from models.document import Chunk
from models.fact import Evidence, Fact
from matching.fact_matcher import candidate_pairs


def _fact(fact_id: str, document: str) -> Fact:
    return Fact(fact_id=fact_id, subject="ENT001", predicate="revenue", value=100, evidence=Evidence(document_id=document, page=1, chunk_id="c", text="Revenue was 100."))


def test_same_entity_predicate_matches_across_documents():
    assert len(candidate_pairs([_fact("a", "d1"), _fact("b", "d2")])) == 1