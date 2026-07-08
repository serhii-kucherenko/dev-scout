from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.models.jam import current_iso_week
from dev_scout.pipeline.runner import run_full_pipeline


def run_week(week: str | None = None, *, use_fixtures: bool = False):
    ctx = RunContext.from_week(week or current_iso_week())
    if not ctx.goal_path().exists():
        _write_default_goal(ctx)
    return run_full_pipeline(ctx, use_fixtures=use_fixtures)


def _write_default_goal(ctx: RunContext) -> None:
    content = f"""# Goal — {ctx.week}

## Mission
Find practical ways to ship faster and build more robust software with AI-assisted dev.

## Research questions
1. What new agent/harness setups have published how-tos and measured speed gains?
2. What CI/testing/review workflows reduced bugs or outage risk this week?
3. What tooling dropped setup time or improved production readiness?

## Sufficiency
- ≥5 JamItems with evidence grade A or B
- Every JamItem has source_url + how_to_steps
- Mix of speed and robustness benefits
- ≥2 corroborated by independent source
"""
    ctx.run_dir.mkdir(parents=True, exist_ok=True)
    ctx.goal_path().write_text(content, encoding="utf-8")
