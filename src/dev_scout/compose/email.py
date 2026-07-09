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


def resolve_repo_url(delivery: dict | None = None) -> str:
    """Repo link shown in every brief. Prefer env, fall back to delivery.yaml."""
    value = os.environ.get("DEV_SCOUT_REPO_URL", "").strip()
    if value:
        return value
    cfg = delivery if delivery is not None else load_yaml(config_dir() / "delivery.yaml")
    return str(cfg.get("repo_url") or "").strip()


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


def select_email_items(
    ctx: RunContext,
    candidates: list[JamItem],
    *,
    limit: int = 5,
    min_items: int = 3,
) -> tuple[list[JamItem], list[JamItem]]:
    """Split ranked candidates into fresh findings and a recap.

    New (never-emailed) findings lead the brief. If there are fewer than
    ``min_items`` of them, previously-seen findings backfill a short recap so a
    brief is never just one line.
    """
    seen = already_mentioned_keys(ctx)
    new_items: list[JamItem] = []
    recap_items: list[JamItem] = []
    local_seen: set[str] = set()
    for item in candidates:
        key = item.canonical_key()
        if key in local_seen:
            continue
        local_seen.add(key)
        if key in seen:
            recap_items.append(item)
        else:
            new_items.append(item)

    shown_new = new_items[:limit]
    backfill = max(0, min(min_items - len(shown_new), limit - len(shown_new)))
    return shown_new, recap_items[:backfill]


def _tag_line(item: JamItem) -> str:
    """Compact benefit / effort / evidence tags so readers can skip fast."""
    return f"{item.benefit.value} · ~{item.setup_cost.value} to set up · grade {item.evidence_grade.value}"


def _format_email_item(index: int, item: JamItem) -> list[str]:
    """Scannable one-finding block: tags + what it's for + one link."""
    lines = [
        f"{index}. {item.title}  [{_tag_line(item)}]",
        f"   Why it matters: {item.why}",
    ]
    try_today = item.try_today.strip()
    if try_today:
        lines.append(f"   Try: {try_today}")
    lines.append(f"   Link: {item.source_url}")
    lines.append("")
    return lines


def _format_recap_item(item: JamItem) -> str:
    return f"- {item.title} [{_tag_line(item)}] — {item.source_url}"


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
            source_url = raw.get("source_url") if isinstance(raw, dict) else None
            if isinstance(source_url, str) and source_url.startswith("http"):
                lines.append(f"- {title} ({benefit}) — {source_url}")
            else:
                lines.append(f"- {title} ({benefit})")
        if len(items) > 5:
            lines.append(f"- …and {len(items) - 5} more")
    lines.append("")
    lines.append("Do not re-read those unless you still need to act on them.")
    lines.append("")
    return lines


def build_email_body(
    day: str,
    new_items: list[JamItem],
    recap_items: list[JamItem] | None = None,
    *,
    previous: dict | None = None,
    repo_url: str = "",
) -> str:
    recap_items = recap_items or []
    lines = [
        f"Dev Scout — {day}",
        "",
        "Mission: ship faster & build more robust software with AI-assisted dev.",
        "",
    ]
    if repo_url:
        lines.extend([f"Repo: {repo_url}", ""])
    lines.extend(_previous_review_lines(previous))

    if not new_items and not recap_items:
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

    if new_items:
        lines.extend(
            [
                f"New since last brief: {len(new_items)} ({_benefit_mix(new_items)}).",
                "Tags read benefit · setup effort · evidence grade — skip anything that doesn't fit.",
                "",
            ]
        )
        for index, item in enumerate(new_items, start=1):
            lines.extend(_format_email_item(index, item))
    else:
        lines.extend(
            [
                "No new jam today.",
                "Nothing new beyond what we already covered in earlier briefs.",
                "",
            ]
        )

    if recap_items:
        lines.append("Recap — recent jam still worth a look:")
        lines.extend(_format_recap_item(item) for item in recap_items)
        lines.append("")

    lines.extend(
        [
            f"Full detail (all steps + evidence): runs/{day}/05-report/daily-digest.md",
            "",
        ]
    )
    return "\n".join(lines)


def run_compose_email(ctx: RunContext) -> EmailDraft:
    delivery = load_yaml(config_dir() / "delivery.yaml")
    ranked = read_json(ctx.stage_path("03-rank") / "ranked.json")
    candidates = [JamItem.model_validate(raw) for raw in ranked.get("items", [])]
    promotable = [item for item in candidates if item.is_promotable()]
    new_items, recap_items = select_email_items(ctx, promotable, limit=5)
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

    body_text = build_email_body(
        ctx.day,
        new_items,
        recap_items,
        previous=previous,
        repo_url=resolve_repo_url(delivery),
    )
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
            "recap_count": len(recap_items),
            "repeated_skipped": max(0, len(promotable) - len(new_items)),
        },
    )
    (email_dir / "email-draft.eml").write_text(_render_eml_draft(draft), encoding="utf-8")
    return draft
