from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.models.jam import EmailDraft, JamItem
from dev_scout.util import config_dir, load_yaml, read_json, write_json


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

    lines = [
        f"Dev Scout — {ctx.day}",
        "",
        "Today: practical ways to ship faster and build safer.",
        "",
    ]

    for index, item in enumerate(top_items, start=1):
        lines.extend(
            [
                f"{index}. {item.title} ({item.benefit.value})",
                f"   Why: {item.why}",
                f"   Source: {item.source_url}",
                f"   How-to: {item.how_to_url or item.source_url}",
                "   Steps:",
            ]
        )
        for step_index, step in enumerate(item.how_to_steps[:5], start=1):
            lines.append(f"     {step_index}. {step}")
        lines.append(f"   Try today: {item.try_today}")
        lines.append("")

    lines.extend(
        [
            "More in the full digest: runs/{day}/05-report/daily-digest.md".format(day=ctx.day),
            "",
        ]
    )

    body_text = "\n".join(lines)
    draft = EmailDraft(
        subject=subject,
        to=delivery.get("recipient", ""),
        body_text=body_text,
        top_items=top_items,
    )

    email_dir = ctx.stage_path("06-email")
    email_dir.mkdir(parents=True, exist_ok=True)
    (email_dir / "email-draft.md").write_text(_render_markdown_draft(draft), encoding="utf-8")
    write_json(email_dir / "email-draft.json", draft.model_dump(mode="json"))
    (email_dir / "email-draft.eml").write_text(_render_eml_draft(draft), encoding="utf-8")
    return draft
