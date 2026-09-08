from collections import Counter

from typing import Any

from models.relationship import Relationship
from models.result import Verdict


def create_verdict(
    facts_count: int,
    relationships: list[Relationship],
    *,
    failures_count: int = 0,
    evidence_coverage: float | None = None,
) -> Verdict:
    labels = (
        "CORROBORATED",
        "CONTRADICTION",
        "CONTEXTUAL_DIFFERENCE",
        "PARTIALLY_CORROBORATED",
        "UNCERTAIN",
        "UNRELATED",
    )
    raw_counts = Counter(relationship.classification for relationship in relationships)
    counts = {label: raw_counts.get(label, 0) for label in labels}
    evaluated = sum(counts[label] for label in labels if label != "UNRELATED")
    contradictions = counts["CONTRADICTION"]
    score = ((counts["CORROBORATED"] + counts["CONTEXTUAL_DIFFERENCE"] + counts["PARTIALLY_CORROBORATED"]) / evaluated) if evaluated else None
    contradiction_rate = contradictions / evaluated if evaluated else 0
    if not relationships:
        label = "INSUFFICIENT EVIDENCE"
    elif contradiction_rate <= 0.05:
        label = "CONSISTENT"
    elif contradiction_rate <= 0.15:
        label = "MOSTLY CONSISTENT"
    elif contradiction_rate <= 0.30:
        label = "MIXED / NEEDS REVIEW"
    else:
        label = "SIGNIFICANT CONTRADICTIONS"
    findings = []
    if contradictions:
        findings.append(f"{contradictions} potentially conflicting relationship{'s' if contradictions != 1 else ''} need review.")
    if counts["CORROBORATED"]:
        findings.append(f"{counts['CORROBORATED']} relationship{'s' if counts['CORROBORATED'] != 1 else ''} were corroborated by independent evidence.")
    if counts["CONTEXTUAL_DIFFERENCE"]:
        findings.append(f"{counts['CONTEXTUAL_DIFFERENCE']} differences were explained by period or scope.")
    if counts["PARTIALLY_CORROBORATED"]:
        findings.append(f"{counts['PARTIALLY_CORROBORATED']} relationships were only partially corroborated because context differed.")
    high_priority = sum(relationship.severity == "HIGH" and relationship.review_required for relationship in relationships)
    coverage_text = f"{evidence_coverage:.0%}" if evidence_coverage is not None else "available"
    if relationships:
        comparison_paragraph = (
            f"The comparison produced {len(relationships)} relationship{'s' if len(relationships) != 1 else ''}: "
            f"{counts['CORROBORATED']} corroborated, {counts['CONTRADICTION']} contradictory, "
            f"{counts['CONTEXTUAL_DIFFERENCE']} contextual difference{'s' if counts['CONTEXTUAL_DIFFERENCE'] != 1 else ''}, "
            f"and {counts['UNCERTAIN']} uncertain. "
            "This separates genuine disagreement from differences caused by reporting period, scope, or definition."
        )
    else:
        comparison_paragraph = (
            "No comparable cross-document relationships were generated. The extracted facts remain available for inspection, "
            "but the current case does not contain enough aligned claims to support a cross-document conclusion."
        )
    if contradictions or counts["UNCERTAIN"]:
        action_paragraph = (
            f"The result should be treated as review-required: {high_priority} high-priority relationship"
            f"{'s' if high_priority != 1 else ''} and {failures_count} validation or data-quality issue"
            f"{'s' if failures_count != 1 else ''} may affect the decision. "
            "Open the Flags & Review and Evidence tabs to verify each conclusion against the cited source text before relying on it."
        )
    else:
        action_paragraph = (
            f"The evidence base is {coverage_text} anchored to source text, and no unresolved contradiction was identified. "
            "The result can be used as a structured starting point, with the Evidence tab available for spot-checking and audit."
        )
    detailed_finding = [
        f"The analysis extracted {facts_count} evidence-grounded fact{'s' if facts_count != 1 else ''} and assessed them across "
        f"{len(relationships)} candidate relationship{'s' if len(relationships) != 1 else ''}. "
        f"Source evidence coverage is {coverage_text}, so the finding is based on traceable document text rather than an unsupported summary.",
        comparison_paragraph,
        action_paragraph,
    ]
    return Verdict(
        label=label,
        consistency_score=score,
        counts=dict(counts),
        high_priority=high_priority,
        summary=f"{facts_count} facts were compared across {len(relationships)} candidate relationships.",
        key_findings=findings or ["No comparable cross-document facts were found."],
        detailed_finding=detailed_finding,
        recommendation="Human review recommended for contradictions and uncertain relationships." if contradictions or counts["UNCERTAIN"] else "No immediate review required for the evaluated relationships.",
    )