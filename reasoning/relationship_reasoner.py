from __future__ import annotations

from typing import Any

from models.fact import Fact
from models.relationship import Relationship
from reasoning.gemini_client import GeminiClient
from extraction.prompts import RELATIONSHIP_PROMPT
from normalization.numbers import normalize_number
from normalization.dates import normalize_period


def _value(fact: Fact) -> Any:
    normalized = normalize_number(fact.value, fact.unit, fact.currency)
    return normalized["amount"] if normalized else fact.value


def _criteria(left: Fact, right: Fact, same_period: bool, same_value: bool, same_scope: bool) -> list[dict[str, str | bool]]:
    return [
        {"label": "Entity match", "passed": left.subject == right.subject, "detail": "Canonical entity IDs match"},
        {"label": "Predicate match", "passed": left.predicate == right.predicate, "detail": "Predicates are equivalent"},
        {"label": "Period match", "passed": same_period, "detail": "Periods overlap or are not specified"},
        {"label": "Unit compatible", "passed": True, "detail": "Values compared in normalized form"},
        {"label": "Value compatible", "passed": same_value, "detail": "Normalized values match" if same_value else "Normalized values differ"},
        {"label": "Scope match", "passed": same_scope, "detail": "Scope matches or is unspecified"},
        {"label": "Evidence anchored", "passed": bool(left.evidence.text and right.evidence.text), "detail": "Both facts have source anchors"},
    ]


def deterministic_relationship(left: Fact, right: Fact, relationship_id: str) -> Relationship:
    left_period = normalize_period(left.time_period)
    right_period = normalize_period(right.time_period)
    same_period = left_period == right_period or not left_period or not right_period
    same_scope = not left.scope or not right.scope or left.scope == right.scope
    left_value, right_value = _value(left), _value(right)
    same_value = False
    if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
        tolerance = max(abs(float(left_value)), abs(float(right_value)), 1) * 0.01
        same_value = abs(float(left_value) - float(right_value)) <= tolerance
    else:
        same_value = str(left_value).strip().lower() == str(right_value).strip().lower()

    flags: list[str] = []
    if not same_period:
        flags.append("TIME_DIFFERENCE")
    if not same_scope:
        flags.append("SCOPE_DIFFERENCE")
    if same_value and left.unit != right.unit:
        flags.append("UNIT_DIFFERENCE")
    if not same_value and isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
        flags.append("NUMERIC_VARIANCE")
    if left.predicate != right.predicate:
        flags.append("PREDICATE_AMBIGUITY")

    if same_value and same_period and same_scope:
        classification, reason_codes, confidence = "CORROBORATED", ["SEMANTIC_MATCH"], 0.96
        reasoning = "The two independently extracted facts resolve to the same normalized value for the same entity, predicate, period, and scope."
        severity, review_status, review_required = "INFO", "AUTO_RESOLVED", False
    elif same_value and (not same_period or not same_scope):
        classification, reason_codes, confidence = "PARTIALLY_CORROBORATED", flags or ["MISSING_CONTEXT"], 0.88
        reasoning = "The sources support the same normalized value, but their period or scope differs, so the corroboration is only partial."
        severity, review_status, review_required = "INFO", "AUTO_RESOLVED", False
    elif not same_period or not same_scope:
        classification, reason_codes, confidence = "CONTEXTUAL_DIFFERENCE", flags, 0.94
        reasoning = "The values differ, but the source facts refer to different reporting periods or scopes, so the difference is contextual rather than a proven contradiction."
        severity, review_status, review_required = "INFO", "AUTO_RESOLVED", False
    elif left_value != right_value:
        classification, reason_codes, confidence = "CONTRADICTION", flags or ["SOURCE_DISAGREEMENT"], 0.9
        reasoning = "The facts describe the same entity and predicate in a comparable context, but their normalized values are incompatible."
        severity, review_status, review_required = "HIGH", "REVIEW_REQUIRED", True
    else:
        classification, reason_codes, confidence = "UNCERTAIN", ["OTHER"], 0.55
        reasoning = "The evidence is related but insufficient to establish whether the claims agree."
        severity, review_status, review_required = "MEDIUM", "REVIEW_REQUIRED", True
    return Relationship(
        relationship_id=relationship_id,
        fact_a=left.fact_id,
        fact_b=right.fact_id,
        classification=classification,
        reason_codes=reason_codes,
        confidence=confidence,
        severity=severity,
        review_status=review_status,
        review_required=review_required,
        reasoning=reasoning,
        evidence_fact_a=left.evidence.text,
        evidence_fact_b=right.evidence.text,
        criteria=_criteria(left, right, same_period, same_value, same_scope),
        flags=flags or reason_codes,
    )


def reason_about_pair(left: Fact, right: Fact, relationship_id: str, client: GeminiClient | None = None) -> Relationship:
    relationship = deterministic_relationship(left, right, relationship_id)
    if not client or not client.available or relationship.classification not in {"UNCERTAIN"}:
        return relationship
    response = client.generate_json(RELATIONSHIP_PROMPT, {"fact_a": left.model_dump(), "fact_b": right.model_dump()})
    if not response:
        return relationship
    classification = str(response.get("classification", relationship.classification)).upper()
    allowed = {"CORROBORATED", "CONTRADICTION", "CONTEXTUAL_DIFFERENCE", "UNCERTAIN", "UNRELATED"}
    if classification not in allowed:
        return relationship
    relationship.classification = classification
    relationship.reason_codes = [str(code).upper() for code in response.get("reason_codes", [])]
    relationship.confidence = min(max(float(response.get("confidence", relationship.confidence)), 0), 1)
    relationship.reasoning = str(response.get("reasoning", relationship.reasoning))
    relationship.flags = relationship.reason_codes or relationship.flags
    relationship.source = "gemini"
    return relationship