from __future__ import annotations

from pathlib import Path

from dev_scout.context import RunContext
from dev_scout.judge.engine import run_judge
from dev_scout.models.jam import current_run_day
from dev_scout.pipeline.runner import run_output_pipeline, run_research_pipeline


def run_goal_loop(
    goal_file: Path | None = None,
    *,
    day: str | None = None,
    max_iterations: int = 3,
    use_fixtures: bool = False,
) -> dict:
    ctx = RunContext.from_day(day or current_run_day())
    ctx.ensure_layout()
    if goal_file and goal_file.exists():
        (ctx.run_dir / "GOAL.md").write_text(goal_file.read_text(encoding="utf-8"), encoding="utf-8")

    iterations = 0
    last_verdict = None
    while iterations < max_iterations:
        iterations += 1
        run_research_pipeline(ctx, use_fixtures=use_fixtures)
        last_verdict = run_judge(ctx)
        if last_verdict.sufficient:
            break
        feedback = ctx.run_dir / f"feedback-{iterations:03d}.md"
        feedback.write_text(
            "\n".join(f"- {gap}" for gap in last_verdict.gaps) + "\n",
            encoding="utf-8",
        )

    assert last_verdict is not None
    result = run_output_pipeline(ctx, last_verdict)
    return {
        "iterations": iterations,
        "sufficient": last_verdict.sufficient,
        "email_path": result.email_path,
    }
