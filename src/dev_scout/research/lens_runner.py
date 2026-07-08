from __future__ import annotations

from pathlib import Path

from dev_scout.context import RunContext
from dev_scout.models.jam import CorroborationStatus, JamItem
from dev_scout.research.lenses import analyze_excerpt, list_lens_ids, load_excerpts, run_lens
from dev_scout.util import write_json


def run_lenses(ctx: RunContext, *, lens_id: str | None = None) -> dict[str, int]:
    ctx.ensure_layout()
    excerpts_path = ctx.research_path("excerpts.jsonl")
    excerpts = load_excerpts(excerpts_path)
    lenses_dir = ctx.research_path("lenses")
    lenses_dir.mkdir(parents=True, exist_ok=True)

    targets = [lens_id] if lens_id else list_lens_ids()
    counts: dict[str, int] = {}

    for target in targets:
        items = run_lens(target, excerpts)
        write_json(
            lenses_dir / target / "output.json",
            {"lens_id": target, "items": [item.model_dump(mode="json") for item in items]},
        )
        counts[target] = len(items)

    return counts


def load_lens_items(ctx: RunContext) -> list[JamItem]:
    items: list[JamItem] = []
    lenses_dir = ctx.research_path("lenses")
    if not lenses_dir.exists():
        return items
    for path in sorted(lenses_dir.glob("*/output.json")):
        payload = __import__("dev_scout.util", fromlist=["read_json"]).read_json(path)
        for raw in payload.get("items", []):
            items.append(JamItem.model_validate(raw))
    return items
