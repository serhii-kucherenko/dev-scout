from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from dev_scout.context import RunContext
from dev_scout.compose.email import resolve_recipient, run_compose_email
from dev_scout.delivery.send import run_send
from dev_scout.judge.engine import run_judge
from dev_scout.models.jam import current_run_day
from dev_scout.pipeline.loop import run_goal_loop
from dev_scout.pipeline.runner import run_full_pipeline, run_research_pipeline
from dev_scout.pipeline.day import run_day
from dev_scout.report.builder import run_report
from dev_scout.research import run_collect, run_corroborate, run_coverage, run_discover, run_lenses
from dev_scout.util import config_dir, load_yaml, project_root

app = typer.Typer(no_args_is_help=True, help="Dev Scout — daily research harness for faster, robust dev")
console = Console()


def _ctx(day: str | None) -> RunContext:
    return RunContext.from_day(day or current_run_day())


def _emit(payload: dict, as_json: bool) -> None:
    if as_json:
        console.print_json(json.dumps(payload))
    else:
        for key, value in payload.items():
            console.print(f"[bold]{key}[/bold]: {value}")


@app.command()
def doctor() -> None:
    """Check config and project layout."""
    root = project_root()
    checks = {
        "project_root": str(root),
        "config": (config_dir() / "judge.yaml").exists(),
        "lenses": len(list((config_dir() / "lenses").glob("*.yaml"))),
        "delivery_mode": load_yaml(config_dir() / "delivery.yaml").get("mode", "draft"),
        "delivery_to": resolve_recipient() or "(unset — set DEV_SCOUT_EMAIL)",
    }
    table = Table(title="Dev Scout Doctor")
    table.add_column("Check")
    table.add_column("Value")
    for key, value in checks.items():
        table.add_row(key, str(value))
    console.print(table)


@app.command()
def discover(
    day: str | None = typer.Option(None, "--day"),
    fixtures: bool = typer.Option(False, "--fixtures", help="Use test fixtures"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    result = run_discover(ctx, use_fixtures=fixtures)
    _emit(result, as_json)


@app.command()
def collect(
    day: str | None = typer.Option(None, "--day"),
    fixtures: bool = typer.Option(False, "--fixtures"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    result = run_collect(ctx, use_fixtures=fixtures)
    _emit(result, as_json)


@app.command("lens")
def lens_cmd(
    day: str | None = typer.Option(None, "--day"),
    lens_id: str | None = typer.Option(None, "--lens"),
    all_lenses: bool = typer.Option(False, "--all"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    if all_lenses:
        result = run_lenses(ctx)
    elif lens_id:
        result = run_lenses(ctx, lens_id=lens_id)
    else:
        result = run_lenses(ctx)
    _emit(result, as_json)


@app.command()
def corroborate(
    day: str | None = typer.Option(None, "--day"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    result = run_corroborate(ctx)
    _emit({"corroboration": result}, as_json)


@app.command()
def coverage(
    day: str | None = typer.Option(None, "--day"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    report = run_coverage(ctx)
    _emit(report.model_dump(mode="json"), as_json)


@app.command()
def judge(
    day: str | None = typer.Option(None, "--day"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    verdict = run_judge(ctx)
    _emit(verdict.model_dump(mode="json"), as_json)


@app.command()
def report(
    day: str | None = typer.Option(None, "--day"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    path = run_report(ctx)
    _emit({"path": path}, as_json)


@app.command("compose-email")
def compose_email(
    day: str | None = typer.Option(None, "--day"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    draft = run_compose_email(ctx)
    _emit({"subject": draft.subject, "to": draft.to, "path": str(ctx.stage_path("06-email") / "email-draft.md")}, as_json)


@app.command()
def send(
    day: str | None = typer.Option(None, "--day"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ctx = _ctx(day)
    result = run_send(ctx, dry_run=dry_run)
    _emit(result, as_json)


@app.command("day")
def day_cmd(
    day: str | None = typer.Option(None, "--day"),
    fixtures: bool = typer.Option(False, "--fixtures", help="Use test fixtures for CI/smoke"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Run full daily pipeline: research → judge → digest + email."""
    result = run_day(day, use_fixtures=fixtures)
    payload = {
        "day": result.day,
        "sufficient": result.verdict.sufficient,
        "digest": result.digest_path,
        "email": result.email_path,
        "run_md": result.run_md_path,
    }
    _emit(payload, as_json)
    if result.email_path:
        console.print(f"\n[green]Email draft:[/green] {result.email_path}")


@app.command()
def loop(
    day: str | None = typer.Option(None, "--day"),
    goal_file: Path | None = typer.Option(None, "--goal-file"),
    max_iterations: int = typer.Option(3, "--max-iterations"),
    fixtures: bool = typer.Option(False, "--fixtures"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Ralph-style loop until research sufficiency or max iterations."""
    result = run_goal_loop(
        goal_file=goal_file,
        day=day,
        max_iterations=max_iterations,
        use_fixtures=fixtures,
    )
    _emit(result, as_json)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
