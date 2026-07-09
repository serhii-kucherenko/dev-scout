from __future__ import annotations

import os

from dev_scout.context import RunContext
from dev_scout.models.jam import EmailDraft, JamItem
from dev_scout.util import config_dir, load_yaml, read_json, write_json


def resolve_recipient(delivery: dict | None = None) -> str:
    """Recipient for email drafts. Prefer env (GitHub Actions / local .env)."""
    for key in ("DEV_SCOUT_EMAIL", "DELIVERY_TO"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    cfg = delivery if delivery is not None else load_yaml(config_dir() / "delivery.yaml")
    return str(cfg.get("recipient") or "").strip()


def _render_markdown_draft(draft: EmailDraft) -> str:
    return "\n".join(
        [
            f"To: {draft.to}",
            f"Subject: {draft.subject}",
            "",
            draft.body_text,
        ]
    )


def _render_eml_draft(draft: EmailDraft) -> str:
    return "\n".join(
        [
            f"To: {draft.to}",
            f"Subject: {draft.subject}",
            "Content-Type: text/plain; charset=utf-8",
            "",
            draft.body_text,
        ]
    )


def _benefit_mix(items: list[JamItem]) -> str:
    speed = sum(1 for item in items if item.benefit.value in {"speed", "both"})
    robustness = sum(1 for item in items if item.benefit.value in {"robustness", "both"})
    return f"speed={speed}, robustness={robustness}"


def _format_email_item(index: int, item: JamItem) -> list[str]:
    """Full jam packet for one finding — matches GOAL / jam-criteria fields."""
    how_to = item.how_to_url or item.source_url
    lines = [
        f"{index}. {item.title}",
        f"   Benefit: {item.benefit.value}",
        f"   Why: {item.why}",
        f"   Evidence: {item.evidence} (grade {item.evidence_grade.value})",
        f"   Setup cost: {item.setup_cost.value}",
        f"   Corroboration: {item.corroboration.value}",
        f"   Lens: {item.lens_id}",
        f"   Source: {item.source_url}",
        f"   How-to: {how_to}",
        "   Steps:",
    ]
    for step_index, step in enumerate(item.how_to_steps, start=1):
        lines.append(f"     {step_index}. {step}")
    try_today = item.try_today.strip() or "Open the source and apply one step on a small branch"
    lines.append(f"   Try today: {try_today}")
    lines.append("")
    return lines


def build_email_body(day: str, items: list[JamItem]) -> str:
    lines = [
        f"Dev Scout — {day}",
        "",
        "Mission: practical ways to ship faster and build more robust software with AI-assisted dev.",
        "",
        f"Today's jam: {len(items)} findings ({_benefit_mix(items)}).",
        "Each item includes source, how-to steps, evidence, and a try-today action.",
        "",
    ]
    for index, item in enumerate(items, start=1):
        lines.extend(_format_email_item(index, item))
    lines.extend(
        [
            f"Full digest: runs/{day}/05-report/daily-digest.md",
            "",
        ]
    )
    return "\n".join(lines)


def run_compose_email(ctx: RunContext) -> EmailDraft:
    delivery = load_yaml(config_dir() / "delivery.yaml")
    ranked = read_json(ctx.stage_path("03-rank") / "ranked.json")
    items = [JamItem.model_validate(raw) for raw in ranked.get("items", [])]
    top_items = [item for item in items if item.is_promotable()][:5]

    subject = delivery.get("subject_template", "Dev Scout {day}").format(
        day=ctx.day,
        week=ctx.day,
        top_count=len(top_items),
    )

    body_text = build_email_body(ctx.day, top_items)
    draft = EmailDraft(
        subject=subject,
        to=resolve_recipient(delivery),
        body_text=body_text,
        top_items=top_items,
    )

    email_dir = ctx.stage_path("06-email")
    email_dir.mkdir(parents=True, exist_ok=True)
    (email_dir / "email-draft.md").write_text(_render_markdown_draft(draft), encoding="utf-8")
    write_json(email_dir / "email-draft.json", draft.model_dump(mode="json"))
    (email_dir / "email-draft.eml").write_text(_render_eml_draft(draft), encoding="utf-8")
    return draft
