from extraction.json_mapper import extract_facts_from_chunk
from models.document import Chunk


class EmptyGeminiResponse:
    def generate_json(self, prompt, payload):
        return {"facts": []}


def test_empty_gemini_fact_response_uses_local_fallback():
    chunk = Chunk(
        chunk_id="c1",
        document_id="d1",
        page_start=1,
        page_end=1,
        text="Acme revenue was INR 25 crore in FY2025.",
    )

    facts = extract_facts_from_chunk(chunk, EmptyGeminiResponse())

    assert facts
    assert facts[0].predicate == "revenue"
    assert facts[0].evidence.text == "Acme revenue was INR 25 crore in FY2025."