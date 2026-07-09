from __future__ import annotations

from dataclasses import dataclass, field

from dev_scout.compose.email import run_compose_email
from dev_scout.context import RunContext
from dev_scout.delivery.send import run_send
from dev_scout.judge.engine import run_judge
from dev_scout.learning.ledger import run_learning
from dev_scout.models.jam import JudgeVerdict
from dev_scout.pipeline.intake import run_intake
from dev_scout.pipeline.run_md import write_run_md
from dev_scout.rank.score import run_rank
from dev_scout.report.builder import run_report
from dev_scout.research import run_collect, run_corroborate, run_coverage, run_discover, run_lenses
from dev_scout.util import write_json


@dataclass
class PipelineResult:
    day: str
    verdict: JudgeVerdict
    email_path: str | None = None
    digest_path: str | None = None
    run_md_path: str | None = None
    send_status: str | None = None
    send_result: dict[str, str] = field(default_factory=dict)


def run_research_pipeline(ctx: RunContext, *, use_fixtures: bool = False) -> None:
    run_intake(ctx)
    run_discover(ctx, use_fixtures=use_fixtures)
    run_collect(ctx, use_fixtures=use_fixtures)
    run_lenses(ctx)
    run_corroborate(ctx)
    run_coverage(ctx)


def run_output_pipeline(ctx: RunContext, verdict: JudgeVerdict) -> PipelineResult:
    result = PipelineResult(day=ctx.day, verdict=verdict)
    if not verdict.sufficient:
        write_run_md(ctx)
        result.run_md_path = str(ctx.run_dir / "RUN.md")
        return result

    run_rank(ctx)
    result.digest_path = run_report(ctx)
    draft = run_compose_email(ctx)
    result.email_path = str(ctx.stage_path("06-email") / "email-draft.md")
    send_result = run_send(ctx)
    result.send_result = send_result
    result.send_status = send_result.get("status")
    run_learning(ctx)
    write_run_md(ctx)
    result.run_md_path = str(ctx.run_dir / "RUN.md")
    write_json(
        ctx.run_dir / "run.manifest.json",
        {
            "day": ctx.day,
            "sufficient": verdict.sufficient,
            "email_to": draft.to,
            "email_subject": draft.subject,
            "email_new_count": len(draft.top_items),
            "digest_path": f"runs/{ctx.day}/05-report/daily-digest.md",
            "email_draft_path": f"runs/{ctx.day}/06-email/email-draft.md",
            "email_json_path": f"runs/{ctx.day}/06-email/email-draft.json",
            "email_eml_path": f"runs/{ctx.day}/06-email/email-draft.eml",
            "send_status": result.send_status,
            "send_result": send_result,
        },
    )
    return result


def run_full_pipeline(ctx: RunContext, *, use_fixtures: bool = False) -> PipelineResult:
    run_research_pipeline(ctx, use_fixtures=use_fixtures)
    verdict = run_judge(ctx)
    return run_output_pipeline(ctx, verdict)
