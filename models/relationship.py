from pydantic import BaseModel, Field


class Relationship(BaseModel):
    relationship_id: str
    fact_a: str
    fact_b: str
    classification: str
    reason_codes: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    severity: str = "INFO"
    review_status: str = "AUTO_RESOLVED"
    review_required: bool = False
    reasoning: str
    evidence_fact_a: str
    evidence_fact_b: str
    criteria: list[dict[str, str | bool]] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    source: str = "deterministic"
    validation_errors: list[str] = Field(default_factory=list)