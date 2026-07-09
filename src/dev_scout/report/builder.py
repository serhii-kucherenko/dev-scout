from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.models.jam import JamItem
from dev_scout.util import read_json, write_json


def _format_item(item: JamItem) -> str:
    steps = "\n".join(f"  {index}. {step}" for index, step in enumerate(item.how_to_steps, start=1))
    how_to = item.how_to_url or item.source_url
    return (
        f"### {item.title}\n\n"
        f"**Why:** {item.why}\n\n"
        f"**Benefit:** {item.benefit.value} | **Grade:** {item.evidence_grade.value}\n\n"
        f"**Evidence:** {item.evidence}\n\n"
        f"**Source:** {item.source_url}\n\n"
        f"**How-to:** {how_to}\n\n"
        f"**Steps:**\n{steps}\n\n"
        f"**Try today:** {item.try_today}\n"
    )


def run_report(ctx: RunContext) -> str:
    ranked = read_json(ctx.stage_path("03-rank") / "ranked.json")
    items = [JamItem.model_validate(raw) for raw in ranked.get("items", [])]
    promotable = [item for item in items if item.is_promotable()]

    lines = [
        f"# Dev Scout Daily Digest — {ctx.day}",
        "",
        "Actionable jam for faster, more robust development.",
        "",
        "## Top jam",
        "",
    ]
    for item in promotable[:5]:
        lines.append(_format_item(item))
        lines.append("")

    lines.extend(["## All findings by lens", ""])
    by_lens: dict[str, list[JamItem]] = {}
    for item in promotable:
        by_lens.setdefault(item.lens_id, []).append(item)
    for lens_id, lens_items in sorted(by_lens.items()):
        lines.append(f"### {lens_id}")
        for item in lens_items:
            lines.append(f"- [{item.title}]({item.source_url})")
        lines.append("")

    verdict = read_json(ctx.stage_path("04-judge") / "verdict.json")
    skipped = verdict.get("skipped") or []
    if skipped:
        lines.extend(["## Skipped", ""])
        lines.extend(f"- {line}" for line in skipped)
        lines.append("")

    content = "\n".join(lines)
    report_dir = ctx.stage_path("05-report")
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "daily-digest.md"
    path.write_text(content, encoding="utf-8")
    return str(path)
