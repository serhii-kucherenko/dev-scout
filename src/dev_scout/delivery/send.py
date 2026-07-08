from __future__ import annotations

import os

import httpx

from dev_scout.context import RunContext
from dev_scout.models.jam import EmailDraft
from dev_scout.util import config_dir, load_yaml, read_json


def run_send(ctx: RunContext, *, dry_run: bool = False) -> dict[str, str]:
    delivery = load_yaml(config_dir() / "delivery.yaml")
    if delivery.get("mode", "draft") != "send" and not dry_run:
        return {"status": "skipped", "reason": "delivery.mode is draft"}

    draft_path = ctx.stage_path("06-email") / "email-draft.json"
    if not draft_path.exists():
        return {"status": "error", "reason": "email draft missing — run compose-email first"}

    draft = EmailDraft.model_validate(read_json(draft_path))
    if dry_run:
        return {"status": "dry_run", "to": draft.to, "subject": draft.subject}

    api_key = os.environ.get("RESEND_API_KEY", "")
    from_addr = os.environ.get("DELIVERY_FROM", "")
    if not api_key or not from_addr:
        return {"status": "error", "reason": "RESEND_API_KEY and DELIVERY_FROM required"}

    with httpx.Client(timeout=30) as client:
        response = client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": from_addr,
                "to": [draft.to],
                "subject": draft.subject,
                "text": draft.body_text,
            },
        )
        response.raise_for_status()
        payload = response.json()

    return {"status": "sent", "id": payload.get("id", "")}
