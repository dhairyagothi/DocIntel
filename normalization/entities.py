import re
from collections import defaultdict

from rapidfuzz.fuzz import ratio

from models.fact import Fact


def canonicalize_name(name: str) -> str:
    value = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    value = re.sub(r"\b(inc|incorporated|ltd|limited|llc|corp|corporation)\b", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def resolve_entities(facts: list[Fact]) -> tuple[list[Fact], list[dict[str, str | float]]]:
    names: list[str] = []
    entity_ids: dict[str, str] = {}
    entities = []
    for fact in facts:
        canonical = canonicalize_name(fact.subject)
        match = next((known for known in names if ratio(canonical, known) >= 88), None)
        if match is None:
            names.append(canonical)
            entity_ids[canonical] = f"ENT{len(names):03d}"
            entities.append({"entity_id": entity_ids[canonical], "canonical_name": fact.subject, "normalized_name": canonical, "confidence": 1.0})
            match = canonical
        fact.subject = entity_ids[match]
        fact.attributes["entity_name"] = next(e["canonical_name"] for e in entities if e["normalized_name"] == match)
    return facts, entities