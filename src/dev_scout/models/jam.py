from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Benefit(str, Enum):
    SPEED = "speed"
    ROBUSTNESS = "robustness"
    BOTH = "both"


class SetupCost(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"


class EvidenceGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class CorroborationStatus(str, Enum):
    SUPPORTED = "supported"
    WEAK = "weak"
    UNSUPPORTED = "unsupported"


class JamItem(BaseModel):
    id: str
    title: str
    why: str
    benefit: Benefit
    source_url: str
    how_to_url: str | None = None
    how_to_steps: list[str] = Field(min_length=1)
    setup_cost: SetupCost
    evidence: str
    evidence_grade: EvidenceGrade
    lens_id: str
    corroboration: CorroborationStatus = CorroborationStatus.WEAK
    try_monday: str = ""

    @field_validator("source_url")
    @classmethod
    def source_must_be_url(cls, value: str) -> str:
        if not value.startswith("http"):
            raise ValueError("source_url must be http(s)")
        return value

    def is_promotable(self) -> bool:
        return (
            self.evidence_grade in {EvidenceGrade.A, EvidenceGrade.B}
            and len(self.how_to_steps) >= 3
            and bool(self.source_url)
        )


class JamDossier(BaseModel):
    week: str
    items: list[JamItem] = Field(default_factory=list)


class JudgeVerdict(BaseModel):
    sufficient: bool
    promoted_count: int
    ab_count: int
    corroborated_count: int
    lenses_with_findings: int
    gaps: list[str] = Field(default_factory=list)
    skipped: list[str] = Field(default_factory=list)


class CoverageReport(BaseModel):
    urls_planned: int = 0
    urls_fetched: int = 0
    urls_extracted: int = 0
    lenses_run: int = 0
    lenses_with_findings: int = 0
    grade_distribution: dict[str, int] = Field(default_factory=dict)
    corroboration_rate: float = 0.0


class EmailDraft(BaseModel):
    subject: str
    to: str
    body_text: str
    body_html: str | None = None
    top_items: list[JamItem] = Field(default_factory=list)


def current_iso_week(reference: date | None = None) -> str:
    today = reference or date.today()
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"
