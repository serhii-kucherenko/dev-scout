from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.models.jam import JamItem
from dev_scout.util import data_dir, read_json, write_json


def _item_key(item: JamItem) -> str:
    return item.source_url


def run_learning(ctx: RunContext) -> dict[str, int]:
    ranked = read_json(ctx.stage_path("03-rank") / "ranked.json")
    items = [JamItem.model_validate(raw) for raw in ranked.get("items", [])]
    promotable = [item for item in items if item.is_promotable()]

    ledger_path = data_dir() / "findings.json"
    ledger = read_json(ledger_path)
    existing = {_item_key(JamItem.model_validate(entry)) for entry in ledger.get("findings", [])}

    new_items = [item for item in promotable if _item_key(item) not in existing]
    prior_week = ledger.get("weeks", [])[-1] if ledger.get("weeks") else None

    delta = {
        "week": ctx.week,
        "prior_week": prior_week,
        "new_count": len(new_items),
        "promoted_count": len(promotable),
        "new_item_ids": [item.id for item in new_items],
    }
    write_json(ctx.stage_path("07-learning") / "delta-vs-last-week.json", delta)

    ledger.setdefault("findings", [])
    ledger.setdefault("weeks", [])
    for item in new_items:
        ledger["findings"].append(item.model_dump(mode="json"))
    if ctx.week not in ledger["weeks"]:
        ledger["weeks"].append(ctx.week)
    write_json(ledger_path, ledger)

    return {"new": len(new_items), "total": len(ledger["findings"])}
