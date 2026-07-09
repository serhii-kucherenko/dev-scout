from __future__ import annotations

from collections import Counter
import re

from dev_scout.context import RunContext
from dev_scout.models.jam import (
    CorroborationStatus,
    CoverageReport,
    JamItem,
    canonicalize_source_url,
)
from dev_scout.research.lens_runner import load_lens_items
from dev_scout.util import read_json, read_jsonl, write_json

STOPWORDS = {
    "with",
    "from",
    "that",
    "this",
    "their",
    "have",
    "into",
    "what",
    "when",
    "where",
    "which",
    "workflow",
    "setup",
    "guide",
    "docs",
    "patterns",
}


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 4 and token not in STOPWORDS
    }


def _independent_support_count(item: JamItem, excerpts: list[dict]) -> int:
    title_tokens = _tokens(item.title)
    if not title_tokens:
        return 0

    item_key = canonicalize_source_url(item.source_url)
    supporting_urls: set[str] = set()
    for excerpt in excerpts:
        url = excerpt.get("url", "")
        if not url.startswith("http"):
            continue
        if canonicalize_source_url(url) == item_key:
            continue
        excerpt_tokens = _tokens(f"{excerpt.get('title', '')} {excerpt.get('text', '')}")
        if len(title_tokens & excerpt_tokens) >= 2:
            supporting_urls.add(canonicalize_source_url(url))
    return len(supporting_urls)


def run_corroborate(ctx: RunContext) -> dict[str, str]:
    items = load_lens_items(ctx)
    excerpts = read_jsonl(ctx.research_path("excerpts.jsonl"))
    results: dict[str, str] = {}

    for item in items:
        independent = _independent_support_count(item, excerpts)
        if independent >= 1:
            status = CorroborationStatus.SUPPORTED
        elif item.evidence_grade.value in {"A", "B", "C"}:
            status = CorroborationStatus.WEAK
        else:
            status = CorroborationStatus.UNSUPPORTED
        results[item.id] = status.value
        item.corroboration = status

    write_json(ctx.research_path("corroboration.json"), results)
    return results


def run_coverage(ctx: RunContext) -> CoverageReport:
    fetch_plan = read_json(ctx.research_path("discover", "fetch-plan.json"))
    collect_summary = read_json(ctx.research_path("collect-summary.json"))
    corroboration = read_json(ctx.research_path("corroboration.json"))
    items = load_lens_items(ctx)

    grade_distribution = Counter(item.evidence_grade.value for item in items)
    lenses_with_findings = len({item.lens_id for item in items})
    supported = sum(1 for value in corroboration.values() if value == CorroborationStatus.SUPPORTED.value)
    rate = supported / len(items) if items else 0.0

    report = CoverageReport(
        urls_planned=int(fetch_plan.get("planned", 0)),
        urls_fetched=int(collect_summary.get("fetched", 0)),
        urls_extracted=int(collect_summary.get("extracted", 0)),
        lenses_run=len(list(ctx.research_path("lenses").glob("*/output.json"))) if ctx.research_path("lenses").exists() else 0,
        lenses_with_findings=lenses_with_findings,
        grade_distribution=dict(grade_distribution),
        corroboration_rate=round(rate, 3),
    )
    write_json(ctx.research_path("coverage.json"), report.model_dump(mode="json"))
    return report
