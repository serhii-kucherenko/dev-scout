from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.util import read_json


def write_run_md(ctx: RunContext) -> str:
    coverage = read_json(ctx.research_path("coverage.json"))
    verdict = read_json(ctx.stage_path("04-judge") / "verdict.json")
    collect = read_json(ctx.research_path("collect-summary.json"))

    lines = [
        f"# Run {ctx.day}",
        "",
        "## Research",
        f"- URLs planned: {coverage.get('urls_planned', 0)}",
        f"- URLs fetched: {coverage.get('urls_fetched', collect.get('fetched', 0))}",
        f"- Excerpts: {coverage.get('urls_extracted', collect.get('extracted', 0))}",
        f"- Lenses with findings: {coverage.get('lenses_with_findings', 0)}",
        f"- Corroboration rate: {coverage.get('corroboration_rate', 0)}",
        "",
        "## Judge",
        f"- Sufficient: {verdict.get('sufficient', False)}",
        f"- Promoted jam: {verdict.get('promoted_count', 0)}",
        "",
        "## Delivery",
        f"- Email draft: `06-email/email-draft.md`",
        f"- Send result: see `06-email/send-result.json` (emailed to `DEV_SCOUT_EMAIL` when secrets are set)",
        "",
        "## Resume",
        "Continue in Cursor chat from the next incomplete stage.",
        "",
    ]
    content = "\n".join(lines)
    ctx.run_dir.mkdir(parents=True, exist_ok=True)
    (ctx.run_dir / "RUN.md").write_text(content, encoding="utf-8")
    return str(ctx.run_dir / "RUN.md")
