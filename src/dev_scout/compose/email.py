from __future__ import annotations

import os
import re
from pathlib import Path

from dev_scout.context import RunContext
from dev_scout.models.jam import EmailDraft, JamItem, canonicalize_source_url
from dev_scout.util import config_dir, data_dir, load_yaml, read_json, runs_dir, write_json


DAY_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LEGACY_WEEK_DIR_RE = re.compile(r"^\d{4}-W\d{2}$")


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


def _is_run_dir_name(name: str) -> bool:
    return bool(DAY_DIR_RE.match(name) or LEGACY_WEEK_DIR_RE.match(name))


def _list_prior_run_dirs(current_day: str, root: Path | None = None) -> list[Path]:
    base = root or runs_dir()
    if not base.exists():
        return []
    dirs = [
        path
        for path in base.iterdir()
        if path.is_dir() and _is_run_dir_name(path.name) and path.name != current_day
    ]
    return sorted(dirs, key=lambda path: path.name)


def load_previous_email(ctx: RunContext) -> dict | None:
    """Most recent prior run's email-draft.json, if any."""
    for path in reversed(_list_prior_run_dirs(ctx.day, ctx.root)):
        draft_path = path / "06-email" / "email-draft.json"
        draft = read_json(draft_path)
        if draft and draft.get("top_items") is not None:
            return {"day": path.name, "draft": draft}
    return None


def already_mentioned_keys(ctx: RunContext) -> set[str]:
    """Source keys already covered in the ledger or any prior emailed brief."""
    keys: set[str] = set()
    ledger = read_json(data_dir() / "findings.json")
    for entry in ledger.get("findings", []):
        url = entry.get("source_url")
        if isinstance(url, str) and url.startswith("http"):
            keys.add(canonicalize_source_url(url))

    for path in _list_prior_run_dirs(ctx.day, ctx.root):
        draft = read_json(path / "06-email" / "email-draft.json")
        for raw in draft.get("top_items") or []:
            url = raw.get("source_url") if isinstance(raw, dict) else None
            if isinstance(url, str) and url.startswith("http"):
                keys.add(canonicalize_source_url(url))
    return keys


def select_new_email_items(ctx: RunContext, candidates: list[JamItem], *, limit: int = 5) -> list[JamItem]:
    seen = already_mentioned_keys(ctx)
    fresh: list[JamItem] = []
    for item in candidates:
        key = item.canonical_key()
        if key in seen:
            continue
        seen.add(key)
        fresh.append(item)
        if len(fresh) >= limit:
            break
    return fresh


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


def _previous_review_lines(previous: dict | None) -> list[str]:
    if not previous:
        return [
            "Previous email: none yet — this is the first brief.",
            "",
        ]

    day = previous["day"]
    draft = previous["draft"]
    items = draft.get("top_items") or []
    lines = [f"Quick review of previous email ({day}):"]
    if not items:
        lines.append("- Previous brief had no new jam items.")
    else:
        for raw in items[:5]:
            title = raw.get("title") or "Untitled"
            benefit = raw.get("benefit") or "?"
            lines.append(f"- {title} ({benefit})")
        if len(items) > 5:
            lines.append(f"- …and {len(items) - 5} more")
    lines.append("")
    lines.append("Do not re-read those unless you still need to act on them.")
    lines.append("")
    return lines


def build_email_body(day: str, items: list[JamItem], *, previous: dict | None = None) -> str:
    lines = [
        f"Dev Scout — {day}",
        "",
        "Mission: practical ways to ship faster and build more robust software with AI-assisted dev.",
        "",
    ]
    lines.extend(_previous_review_lines(previous))

    if not items:
        lines.extend(
            [
                "No new jam today.",
                "Nothing new beyond what we already covered in earlier briefs.",
                "",
                f"Full digest (if research ran): runs/{day}/05-report/daily-digest.md",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            f"New jam today: {len(items)} findings ({_benefit_mix(items)}).",
            "Only items not covered in earlier emails. Each includes source, how-to, evidence, and try-today.",
            "",
        ]
    )
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
    candidates = [JamItem.model_validate(raw) for raw in ranked.get("items", [])]
    promotable = [item for item in candidates if item.is_promotable()]
    new_items = select_new_email_items(ctx, promotable, limit=5)
    previous = load_previous_email(ctx)

    if new_items:
        default_subject = "Dev Scout {day} — {top_count} new ways to ship faster / build safer"
    else:
        default_subject = "Dev Scout {day} — no new jam"
    subject = delivery.get("subject_template", default_subject).format(
        day=ctx.day,
        week=ctx.day,
        top_count=len(new_items),
    )
    if not new_items:
        subject = f"Dev Scout {ctx.day} — no new jam"

    body_text = build_email_body(ctx.day, new_items, previous=previous)
    draft = EmailDraft(
        subject=subject,
        to=resolve_recipient(delivery),
        body_text=body_text,
        top_items=new_items,
    )

    email_dir = ctx.stage_path("06-email")
    email_dir.mkdir(parents=True, exist_ok=True)
    (email_dir / "email-draft.md").write_text(_render_markdown_draft(draft), encoding="utf-8")
    write_json(
        email_dir / "email-draft.json",
        {
            **draft.model_dump(mode="json"),
            "previous_day": previous["day"] if previous else None,
            "new_count": len(new_items),
            "repeated_skipped": max(0, len(promotable) - len(new_items)),
        },
    )
    (email_dir / "email-draft.eml").write_text(_render_eml_draft(draft), encoding="utf-8")
    return draft
