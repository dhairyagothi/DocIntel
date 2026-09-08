from __future__ import annotations

import json
import re
from typing import Any

from extraction.prompts import FACT_EXTRACTION_PROMPT
from models.document import Chunk
from models.fact import Evidence, Fact
from reasoning.gemini_client import GeminiClient
from utils.hashing import stable_id


def _number_from_text(text: str) -> tuple[Any, str | None, str | None]:
    match = re.search(
        r"(?i)(₹|rs\.?|inr|\$|€|£)?\s*([\d][\d,]*(?:\.\d+)?)\s*(%|million|mn|billion|bn|crore|cr|lakh|k)?",
        text,
    )
    if not match:
        return None, None, None
    currency_map = {"₹": "INR", "rs": "INR", "rs.": "INR", "inr": "INR", "$": "USD", "€": "EUR", "£": "GBP"}
    return float(match.group(2).replace(",", "")), match.group(3), currency_map.get((match.group(1) or "").lower())


def _heuristic_facts(chunk: Chunk) -> list[dict[str, Any]]:
    facts = []
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", chunk.text) if s.strip()]
    for sentence in sentences:
        if not re.search(r"\d|%|is |was |were |reached|increased|decreased|appointed|founded|acquired", sentence, re.I):
            continue
        number, unit, currency = _number_from_text(sentence)
        words = re.split(r"\s+", sentence)
        subject = " ".join(words[: min(4, len(words))]).strip(" ,:;")
        predicate_match = re.search(
            r"\b(revenue|profit|income|sales|employees?|customers?|growth|market share|capacity|debt|"
            r"founded|headquarters|ceo|founder|acquired|appointed|production|assets?|liabilities?|"
            r"beds?|consumption|certification|patent)\b",
            sentence,
            re.I,
        )
        predicate = predicate_match.group(1).lower().replace(" ", "_") if predicate_match else "claim"
        date_match = re.search(r"\b(?:FY\s*)?20\d{2}\b|\bQ[1-4]\s*FY?\s*'?\d{2,4}\b", sentence, re.I)
        value: Any = number if number is not None else sentence
        facts.append({
            "subject": subject,
            "predicate": predicate,
            "value": value,
            "unit": unit,
            "currency": currency,
            "time_period": date_match.group(0) if date_match else None,
            "scope": "company" if predicate not in {"claim", "founded", "headquarters"} else None,
            "evidence_text": sentence,
            "confidence": 0.62 if number is not None else 0.55,
        })
    return facts[:25]


def extract_facts_from_chunk(chunk: Chunk, client: GeminiClient | None = None) -> list[Fact]:
    payload = {"chunk_id": chunk.chunk_id, "document_id": chunk.document_id, "page": chunk.page_start, "text": chunk.text}
    response = client.generate_json(FACT_EXTRACTION_PROMPT, payload) if client else None
    gemini_facts = response.get("facts", []) if response and isinstance(response.get("facts"), list) else []
    usable_gemini_facts = [
        item for item in gemini_facts
        if isinstance(item, dict)
        and str(item.get("predicate", "")).strip()
        and str(item.get("evidence_text", "")).strip()
    ]
    # Gemini can return valid JSON with an empty or partially malformed facts
    # array. Keep the local extractor as a safety net so one weak model response
    # cannot erase evidence from the rest of the pipeline.
    raw_facts = usable_gemini_facts or _heuristic_facts(chunk)
    facts: list[Fact] = []
    for index, raw in enumerate(raw_facts):
        if not isinstance(raw, dict) or not str(raw.get("predicate", "")).strip() or not str(raw.get("evidence_text", "")).strip():
            continue
        evidence_text = str(raw["evidence_text"])
        evidence = Evidence(document_id=chunk.document_id, page=chunk.page_start, chunk_id=chunk.chunk_id, text=evidence_text)
        facts.append(Fact(
            fact_id=stable_id("FACT", chunk.chunk_id, str(index), str(raw.get("predicate"))),
            subject=str(raw.get("subject") or "Unknown entity"),
            predicate=str(raw.get("predicate")).strip().lower().replace(" ", "_"),
            value=raw.get("value"),
            unit=raw.get("unit"),
            currency=raw.get("currency"),
            time_period=raw.get("time_period"),
            scope=raw.get("scope"),
            evidence=evidence,
            confidence=float(raw.get("confidence", 0.65)),
            attributes={k: v for k, v in raw.items() if k not in {"subject", "predicate", "value", "unit", "currency", "time_period", "scope", "evidence_text", "confidence"}},
        ))
    return facts