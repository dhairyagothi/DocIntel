from typing import Any

from pydantic import BaseModel, Field


class Verdict(BaseModel):
    label: str
    consistency_score: float | None = None
    counts: dict[str, int] = Field(default_factory=dict)
    high_priority: int = 0
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    detailed_finding: list[str] = Field(default_factory=list)
    recommendation: str


class ProcessingResult(BaseModel):
    metadata: dict[str, Any] = Field(default_factory=dict)
    documents: list[dict[str, Any]] = Field(default_factory=list)
    entities: list[dict[str, Any]] = Field(default_factory=list)
    facts: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    flags: list[dict[str, Any]] = Field(default_factory=list)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    failures: list[dict[str, Any]] = Field(default_factory=list)
    verdict: dict[str, Any] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)
    processing: dict[str, Any] = Field(default_factory=dict)