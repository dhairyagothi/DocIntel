from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from typing import BinaryIO, Callable

from extraction.candidate_detector import detect_candidate_chunks
from extraction.json_mapper import extract_facts_from_chunk
from ingestion.chunker import create_chunks
from ingestion.cleaner import clean_document
from ingestion.pdf_parser import extract_pdf
from matching.fact_matcher import candidate_pairs
from models.document import Chunk, Document
from models.fact import Fact
from models.result import ProcessingResult
from pipeline.stages import STAGES
from normalization.dates import normalize_period
from normalization.entities import resolve_entities
from normalization.numbers import normalize_number
from normalization.units import normalize_unit
from reasoning.gemini_client import GeminiClient
from reasoning.relationship_reasoner import reason_about_pair
from reasoning.verdict_engine import create_verdict
from utils.logger import log_stage
from validation.evidence_validator import validate_relationship
from validation.failure_detector import detect_failures
from database.store import persist


def _input_name(item: tuple[str, bytes] | BinaryIO) -> tuple[str, bytes]:
    if isinstance(item, tuple):
        return item
    return getattr(item, "name", "uploaded.pdf"), item.getvalue()


def _normalize_facts(facts: list[Fact]) -> list[Fact]:
    for fact in facts:
        fact.unit = normalize_unit(fact.unit)
        number = normalize_number(fact.value, fact.unit, fact.currency)
        fact.normalized_value = number["amount"] if number else fact.value
        period = normalize_period(fact.time_period)
        fact.time_period = json.dumps(period, sort_keys=True) if period else fact.time_period
    return facts


def process_documents(
    files: list[tuple[str, bytes] | BinaryIO],
    on_stage: Callable[[int, str, dict], None] | None = None,
    on_log: Callable[[str], None] | None = None,
) -> ProcessingResult:
    logs: list[str] = []
    documents: list[Document] = []
    chunks: list[Chunk] = []
    facts: list[Fact] = []
    def stage(index: int, name: str, payload: dict | None = None) -> None:
        if on_stage:
            on_stage(index, name, payload or {})

    stage(0, "PDF Extraction")
    for item in files:
        filename, payload = _input_name(item)
        document = extract_pdf(payload, filename)
        documents.append(document)
        log_stage(logs, f"Loaded {filename} ({document.page_count} pages)", on_log)
    stage(1, "Document Structuring", {"documents": len(documents), "pages": sum(d.page_count for d in documents)})
    for document in documents:
        clean_document(document)
        created = create_chunks(document)
        chunks.extend(created)
        log_stage(logs, f"Created {len(created)} evidence chunks for {document.filename}", on_log)
    stage(2, "JSON Mapping", {"chunks": len(chunks)})
    client = GeminiClient()
    candidate_chunks = detect_candidate_chunks(chunks)
    for chunk in candidate_chunks:
        facts.extend(extract_facts_from_chunk(chunk, client))
    log_stage(logs, f"Extracted {len(facts)} candidate facts ({'Gemini + fallback' if client.available else 'local fallback'})", on_log)
    stage(3, "Entity Resolution")
    facts, entities = resolve_entities(facts)
    stage(4, "Fact Normalization")
    facts = _normalize_facts(facts)
    log_stage(logs, f"Normalized {len(facts)} facts and resolved {len(entities)} entities", on_log)
    stage(5, "Relationship Discovery")
    pairs = candidate_pairs(facts)
    log_stage(logs, f"Identified {len(pairs)} candidate fact pairs", on_log)
    stage(6, "Semantic Reasoning")
    relationships = [
        reason_about_pair(left, right, f"REL_{index:03d}", client)
        for index, (left, right) in enumerate(pairs, start=1)
    ]
    if relationships:
        log_stage(logs, f"Analyzed {len(relationships)} relationships", on_log)
    stage(7, "Evidence Validation")
    fact_map = {fact.fact_id: fact for fact in facts}
    document_map = {document.document_id: document for document in documents}
    relationships = [validate_relationship(item, fact_map, document_map) for item in relationships]
    failures = detect_failures(facts, documents)
    log_stage(logs, f"Validated {len(relationships)} relationships and flagged {len(failures)} issues", on_log)
    evidence_coverage = (sum(bool(fact.evidence.text and fact.evidence.page) for fact in facts) / len(facts)) if facts else 0
    stage(8, "Final Verdict")
    verdict = create_verdict(
        len(facts),
        relationships,
        failures_count=len(failures),
        evidence_coverage=evidence_coverage,
    )
    log_stage(logs, f"Final verdict: {verdict.label}", on_log)
    fact_map = {fact.fact_id: fact for fact in facts}
    flag_counts = Counter(flag for relationship in relationships for flag in relationship.flags)
    flags = [{"flag": flag, "count": count} for flag, count in sorted(flag_counts.items())]
    issues = []
    for relationship in relationships:
        if relationship.review_required or relationship.severity in {"HIGH", "MEDIUM"}:
            left = fact_map.get(relationship.fact_a)
            predicate = (left.predicate if left else "fact").replace("_", " ")
            issues.append({
                "issue_id": relationship.relationship_id,
                "severity": relationship.severity,
                "type": relationship.classification,
                "title": f"{predicate.title()} requires review",
                "reason": relationship.reasoning,
                "confidence": relationship.confidence,
                "relationship_id": relationship.relationship_id,
                "status": relationship.review_status,
            })
    for index, failure in enumerate(failures, start=1):
        issues.append({
            "issue_id": f"FAIL_{index:03d}",
            "severity": "MEDIUM" if failure.get("severity") == "high" else "LOW",
            "type": failure.get("type", "DATA_QUALITY"),
            "title": "Extraction or data-quality warning",
            "reason": failure.get("message", ""),
            "confidence": None,
            "relationship_id": None,
            "status": "REVIEW_REQUIRED",
        })
    evidence = [
        {
            "fact_id": fact.fact_id,
            "document_id": fact.evidence.document_id,
            "page": fact.evidence.page,
            "chunk_id": fact.evidence.chunk_id,
            "text": fact.evidence.text,
        }
        for fact in facts
    ]
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1.0",
        "documents": len(documents),
        "pages": sum(document.page_count for document in documents),
        "chunks": len(chunks),
        "gemini_enabled": client.available,
        "evidence_coverage": evidence_coverage,
        "page_anchors": sum(bool(fact.evidence.page) for fact in facts),
        "high_confidence_facts": sum(fact.confidence >= 0.8 for fact in facts),
        "missing_context": sum(not fact.time_period or not fact.scope for fact in facts),
        "duplicate_facts": sum(1 for item in failures if item.get("type") == "DUPLICATE_FACT"),
    }
    persist(documents, chunks, facts, relationships)
    result = ProcessingResult(
        metadata=metadata,
        documents=[document.model_dump() for document in documents],
        entities=entities,
        facts=[fact.model_dump() for fact in facts],
        relationships=[relationship.model_dump() for relationship in relationships],
        flags=flags,
        issues=issues,
        evidence=evidence,
        failures=failures,
        verdict=verdict.model_dump(),
        logs=logs,
        processing={"stages": [{"name": name, "status": "complete"} for name in STAGES], "logs": logs},
    )
    return result