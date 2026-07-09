from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.util import data_dir, read_json, write_json


def run_intake(ctx: RunContext) -> None:
    ctx.ensure_layout()
    ledger = read_json(data_dir() / "findings.json")
    goal_exists = ctx.goal_path().exists()
    write_json(
        ctx.stage_path("00-intake") / "intake.json",
        {
            "day": ctx.day,
            "goal_present": goal_exists,
            "prior_findings": len(ledger.get("findings", [])),
            "prior_days": ledger.get("days", ledger.get("weeks", [])),
        },
    )
