from __future__ import annotations

from collections import Counter

from dev_scout.context import RunContext
from dev_scout.models.jam import CorroborationStatus, CoverageReport, JamItem
from dev_scout.research.lens_runner import load_lens_items
from dev_scout.util import read_json, read_jsonl, write_json


def run_corroborate(ctx: RunContext) -> dict[str, str]:
    items = load_lens_items(ctx)
    excerpts = read_jsonl(ctx.research_path("excerpts.jsonl"))
    excerpt_urls = {row.get("url") for row in excerpts}
    results: dict[str, str] = {}

    for item in items:
        independent = sum(
            1
            for url in excerpt_urls
            if url and url != item.source_url and item.lens_id in (url or "")
        )
        if independent >= 1 or item.evidence_grade.value in {"A", "B"}:
            status = CorroborationStatus.SUPPORTED
        elif item.evidence_grade.value == "C":
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
