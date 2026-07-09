from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.models.jam import JamDossier
from dev_scout.research.lens_runner import load_lens_items
from dev_scout.util import write_json


def run_synthesize(ctx: RunContext) -> JamDossier:
    items = load_lens_items(ctx)
    dossier = JamDossier(day=ctx.day, items=items)
    write_json(
        ctx.stage_path("02-synthesize") / "dossier.json",
        dossier.model_dump(mode="json"),
    )
    return dossier
