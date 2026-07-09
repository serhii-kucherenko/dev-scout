from __future__ import annotations

from datetime import date
from enum import Enum
import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import BaseModel, Field, field_validator, model_validator


TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def canonicalize_source_url(url: str) -> str:
    parts = urlsplit(url)
    filtered_query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith(TRACKING_QUERY_PREFIXES)
        and key.lower() not in TRACKING_QUERY_KEYS
    ]
    normalized = parts._replace(
        scheme=parts.scheme.lower(),
        netloc=parts.netloc.lower(),
        path=parts.path.rstrip("/") or "/",
        query=urlencode(filtered_query, doseq=True),
        fragment="",
    )
    return urlunsplit(normalized)


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
    try_today: str = ""

    @model_validator(mode="before")
    @classmethod
    def _migrate_try_monday(cls, data: Any) -> Any:
        if isinstance(data, dict) and "try_today" not in data and "try_monday" in data:
            migrated = dict(data)
            migrated["try_today"] = migrated.pop("try_monday")
            return migrated
        return data

    @field_validator("source_url")
    @classmethod
    def source_must_be_url(cls, value: str) -> str:
        if not value.startswith("http"):
            raise ValueError("source_url must be http(s)")
        return value

    def uses_generated_source_url(self) -> bool:
        parts = urlsplit(self.source_url)
        return parts.netloc == "example.com" and parts.path.startswith("/dev-scout/")

    def has_concrete_steps(self) -> bool:
        if len(self.how_to_steps) < 3:
            return False
        normalized = [re.sub(r"\s+", " ", step.strip().lower()) for step in self.how_to_steps[:4]]
        template_prefixes = [
            "open the source:",
            "skim for prerequisites and install commands",
            "apply the workflow on a small branch before team rollout",
            "measure cycle time or defect rate for one week",
        ]
        return not all(
            step.startswith(template)
            for step, template in zip(normalized, template_prefixes, strict=False)
        )

    def canonical_key(self) -> str:
        return canonicalize_source_url(self.source_url)

    def is_promotable(self) -> bool:
        return (
            self.evidence_grade in {EvidenceGrade.A, EvidenceGrade.B}
            and self.has_concrete_steps()
            and bool(self.source_url)
            and not self.uses_generated_source_url()
        )


class JamDossier(BaseModel):
    day: str
    items: list[JamItem] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _migrate_week(cls, data: Any) -> Any:
        if isinstance(data, dict) and "day" not in data and "week" in data:
            migrated = dict(data)
            migrated["day"] = migrated.pop("week")
            return migrated
        return data


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


def current_run_day(reference: date | None = None) -> str:
    today = reference or date.today()
    return today.isoformat()
