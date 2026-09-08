from __future__ import annotations

from itertools import combinations

from matching.similarity import text_similarity
from models.fact import Fact


def candidate_pairs(facts: list[Fact]) -> list[tuple[Fact, Fact]]:
    pairs = []
    for left, right in combinations(facts, 2):
        if left.evidence.document_id == right.evidence.document_id:
            continue
        same_entity = left.subject == right.subject
        predicate_score = text_similarity(left.predicate, right.predicate)
        if same_entity and predicate_score >= 0.72:
            pairs.append((left, right))
    return pairs