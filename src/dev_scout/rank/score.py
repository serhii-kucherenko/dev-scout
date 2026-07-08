from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.models.jam import EvidenceGrade, JamItem, SetupCost
from dev_scout.synthesis.merge import run_synthesize
from dev_scout.util import data_dir, read_json, write_json


GRADE_WEIGHT = {"A": 4, "B": 3, "C": 2, "D": 1}
COST_WEIGHT = {"minutes": 3, "hours": 2, "days": 1}


def _score(item: JamItem, known_ids: set[str]) -> float:
    grade = GRADE_WEIGHT.get(item.evidence_grade.value, 0)
    cost = COST_WEIGHT.get(item.setup_cost.value, 1)
    novelty = 2.0 if item.id not in known_ids else 0.5
    benefit = 1.5 if item.benefit.value == "both" else 1.0
    return grade * cost * novelty * benefit


def run_rank(ctx: RunContext) -> list[JamItem]:
    dossier = run_synthesize(ctx)
    ledger = read_json(data_dir() / "findings.json")
    known_ids = {entry.get("id") for entry in ledger.get("findings", [])}

    ranked = sorted(dossier.items, key=lambda item: _score(item, known_ids), reverse=True)
    write_json(
        ctx.stage_path("03-rank") / "ranked.json",
        {"week": ctx.week, "items": [item.model_dump(mode="json") for item in ranked]},
    )
    return ranked
