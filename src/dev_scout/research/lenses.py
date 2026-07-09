from __future__ import annotations

import re
from typing import Any

from dev_scout.models.jam import Benefit, EvidenceGrade, JamItem, SetupCost
from dev_scout.util import config_dir, load_yaml, read_jsonl


def _score_text(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered)


def _grade_from_signals(has_metric: bool, has_repo: bool, steps_count: int, tier: str) -> EvidenceGrade:
    score = 0
    if has_metric:
        score += 25
    if has_repo:
        score += 20
    if steps_count >= 3:
        score += 20
    if tier == "primary":
        score += 15
    if score >= 75:
        return EvidenceGrade.A
    if score >= 55:
        return EvidenceGrade.B
    if score >= 35:
        return EvidenceGrade.C
    return EvidenceGrade.D


def _clean_step(step: str) -> str:
    return re.sub(r"\s+", " ", step).strip(" \t\r\n-:;,.")


def _build_steps(text: str) -> list[str]:
    numbered = [
        _clean_step(step)
        for step in re.findall(r"(?:^|\n)\s*(?:\d+[\).\s]+|-\s+)(.+)", text)
    ]
    if len(numbered) >= 3:
        return numbered[:7]

    inline_numbered = [
        _clean_step(step)
        for step in re.findall(r"(?:^|[\s:])\d+[\.\)]\s*(.*?)(?=(?:\s+\d+[\.\)])|$)", text)
    ]
    if len(inline_numbered) >= 3:
        return inline_numbered[:7]

    labelled = re.search(r"(?:steps?|setup)\s*:\s*(.+)", text, re.I)
    if labelled:
        segments = [
            _clean_step(step)
            for step in re.split(r"\s*(?:,|;|\band\b)\s*", labelled.group(1))
        ]
        concrete = [step for step in segments if step]
        if len(concrete) >= 3:
            return concrete[:7]

    return []


def _has_metric(text: str) -> bool:
    return bool(re.search(r"\d+\s*%|\d+x|\d+\s*(ms|sec|min|hours|days|bugs|PRs)", text, re.I))


def analyze_excerpt(
    excerpt: dict[str, Any],
    lens_id: str,
    lens_cfg: dict[str, Any],
    index: int,
) -> JamItem | None:
    text = excerpt.get("text", "")
    url = excerpt.get("url", "")
    if excerpt.get("lens_id") and excerpt.get("lens_id") != lens_id:
        return None
    keywords = lens_cfg.get("keywords") or []
    if _score_text(text, keywords) == 0 and not url.startswith("search://"):
        return None

    benefit_raw = lens_cfg.get("benefit", "both")
    benefit = Benefit(benefit_raw)
    title = excerpt.get("title") or f"{lens_id} finding {index}"
    if not url.startswith("http"):
        return None
    steps = _build_steps(text)
    if len(steps) < 3:
        return None
    has_repo = "github.com" in url
    tier = excerpt.get("tier", "secondary")
    grade = _grade_from_signals(_has_metric(text), has_repo, len(steps), tier)

    source_url = url
    return JamItem(
        id=f"{lens_id}-{index}",
        title=title[:140],
        why=lens_cfg.get("question", "Relevant to daily dev improvements"),
        benefit=benefit,
        source_url=source_url,
        how_to_url=source_url,
        how_to_steps=steps,
        setup_cost=SetupCost.HOURS,
        evidence=lens_cfg.get("required_evidence", "Documented outcome"),
        evidence_grade=grade,
        lens_id=lens_id,
        try_today=steps[0] if steps else "Review the linked source",
    )


def run_lens(lens_id: str, excerpts: list[dict[str, Any]]) -> list[JamItem]:
    lens_cfg = load_yaml(config_dir() / "lenses" / f"{lens_id}.yaml")
    if not lens_cfg:
        return []

    items: list[JamItem] = []
    for index, excerpt in enumerate(excerpts, start=1):
        item = analyze_excerpt(excerpt, lens_id, lens_cfg, index)
        if item:
            items.append(item)
    return items


def list_lens_ids() -> list[str]:
    lens_dir = config_dir() / "lenses"
    return sorted(path.stem for path in lens_dir.glob("*.yaml"))


def load_excerpts(path) -> list[dict[str, Any]]:
    return read_jsonl(path)
