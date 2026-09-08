from typing import Any

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    document_id: str
    page: int
    chunk_id: str
    text: str


class Fact(BaseModel):
    fact_id: str
    subject: str
    predicate: str
    value: Any
    normalized_value: Any = None
    unit: str | None = None
    currency: str | None = None
    time_period: str | None = None
    scope: str | None = None
    evidence: Evidence
    confidence: float = Field(default=0.7, ge=0, le=1)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @property
    def display_value(self) -> str:
        value = self.value
        suffix = f" {self.unit}" if self.unit else ""
        currency = f"{self.currency} " if self.currency else ""
        return f"{currency}{value}{suffix}".strip()