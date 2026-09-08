import re

from models.document import Chunk

FACT_TERMS = {
    "revenue", "profit", "ebitda", "employees", "employee", "ceo", "founder",
    "founded", "acquired", "headquarters", "market share", "growth", "customers",
    "funding", "debt", "production", "capacity", "sales", "income", "assets",
    "liability", "appointed", "certified", "patent", "beds", "consumption",
}
NUMBER_RE = re.compile(r"(?i)(?:₹|rs\.?|inr|\$|€|£)?\s*[\d][\d,]*(?:\.\d+)?\s*(?:%|million|mn|billion|bn|crore|cr|lakh|k)?")


def detect_candidate_chunks(chunks: list[Chunk]) -> list[Chunk]:
    candidates = []
    for chunk in chunks:
        lowered = chunk.text.lower()
        score = bool(NUMBER_RE.search(chunk.text)) + sum(term in lowered for term in FACT_TERMS)
        if score or len(chunks) <= 8:
            candidates.append(chunk)
    return candidates or chunks