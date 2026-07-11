from __future__ import annotations

import os

import httpx

from dev_scout.compose.email import resolve_recipient
from dev_scout.context import RunContext
from dev_scout.models.jam import EmailDraft
from dev_scout.util import config_dir, load_yaml, read_json, write_json, write_json_with_secret_allowlist


def _delivery_mode(delivery: dict) -> str:
    configured = str(delivery.get("mode") or "send").strip().lower()
    if configured in {"send", "draft"}:
        return configured
    return "send"


def run_send(ctx: RunContext, *, dry_run: bool = False) -> dict[str, str]:
    """Send the findings email draft to DEV_SCOUT_EMAIL via Resend."""
    delivery = load_yaml(config_dir() / "delivery.yaml")
    mode = _delivery_mode(delivery)
    if mode != "send" and not dry_run:
        result = {"status": "skipped", "reason": "delivery.mode is draft"}
        _write_send_result(ctx, result)
        return result

    draft_path = ctx.stage_path("06-email") / "email-draft.json"
    if not draft_path.exists():
        result = {"status": "error", "reason": "email draft missing — run compose-email first"}
        _write_send_result(ctx, result)
        return result

    draft = EmailDraft.model_validate(read_json(draft_path))
    recipient = draft.to.strip() or resolve_recipient(delivery)
    if not recipient:
        result = {
            "status": "error",
            "reason": "DEV_SCOUT_EMAIL (or DELIVERY_TO) is required to send findings",
        }
        _write_send_result(ctx, result)
        return result

    if dry_run:
        result = {"status": "dry_run", "to": recipient, "subject": draft.subject}
        _write_send_result(ctx, result)
        return result

    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    from_addr = os.environ.get("DELIVERY_FROM", "").strip()
    if not api_key or not from_addr:
        result = {
            "status": "skipped",
            "reason": "RESEND_API_KEY and DELIVERY_FROM required to send",
            "to": recipient,
            "subject": draft.subject,
        }
        _write_send_result(ctx, result)
        return result

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "from": from_addr,
                    "to": [recipient],
                    "subject": draft.subject,
                    "text": draft.body_text,
                },
            )
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:  # noqa: BLE001 — surface send failure without crashing the run
        result = {
            "status": "error",
            "reason": str(exc),
            "to": recipient,
            "subject": draft.subject,
        }
        _write_send_result(ctx, result)
        return result

    result = {
        "status": "sent",
        "id": str(payload.get("id", "")),
        "to": recipient,
        "subject": draft.subject,
    }
    _write_send_result(ctx, result)
    return result


def _write_send_result(ctx: RunContext, result: dict[str, str]) -> None:
    email_dir = ctx.stage_path("06-email")
    email_dir.mkdir(parents=True, exist_ok=True)
    if "to" in result:
        write_json_with_secret_allowlist(email_dir / "send-result.json", result, "to")
        return
    write_json(email_dir / "send-result.json", result)
