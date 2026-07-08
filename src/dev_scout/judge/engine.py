from __future__ import annotations

from dev_scout.context import RunContext
from dev_scout.models.jam import CorroborationStatus, EvidenceGrade, JamItem, JudgeVerdict
from dev_scout.rank.score import run_rank
from dev_scout.util import config_dir, load_yaml, read_json, write_json


def _load_corroboration(ctx: RunContext) -> dict[str, str]:
    return read_json(ctx.research_path("corroboration.json"))


def run_judge(ctx: RunContext) -> JudgeVerdict:
    cfg = load_yaml(config_dir() / "judge.yaml")
    ranked_path = ctx.stage_path("03-rank") / "ranked.json"
    if not ranked_path.exists():
        run_rank(ctx)

    payload = read_json(ranked_path)
    items = [JamItem.model_validate(raw) for raw in payload.get("items", [])]
    corroboration = _load_corroboration(ctx)

    promotable = [item for item in items if item.is_promotable()]
    ab_items = [
        item
        for item in promotable
        if item.evidence_grade in {EvidenceGrade.A, EvidenceGrade.B}
    ]
    corroborated = [
        item
        for item in promotable
        if corroboration.get(item.id) == CorroborationStatus.SUPPORTED.value
    ]
    lenses = {item.lens_id for item in promotable}

    gaps: list[str] = []
    skipped: list[str] = []

    if len(ab_items) < int(cfg.get("min_ab_grade", 5)):
        gaps.append(f"Need more A/B jam items ({len(ab_items)}/{cfg.get('min_ab_grade', 5)})")
    if len(corroborated) < int(cfg.get("min_corroborated", 2)):
        gaps.append(
            f"Need more corroborated items ({len(corroborated)}/{cfg.get('min_corroborated', 2)})"
        )
    if len(lenses) < int(cfg.get("min_lenses_with_findings", 3)):
        gaps.append(
            f"Need broader lens coverage ({len(lenses)}/{cfg.get('min_lenses_with_findings', 3)})"
        )

    for item in items:
        if not item.is_promotable():
            skipped.append(f"{item.title}: missing link, steps, or grade")

    sufficient = not gaps and len(promotable) >= int(cfg.get("min_jam_items", 5))
    verdict = JudgeVerdict(
        sufficient=sufficient,
        promoted_count=len(promotable),
        ab_count=len(ab_items),
        corroborated_count=len(corroborated),
        lenses_with_findings=len(lenses),
        gaps=gaps,
        skipped=skipped[:10],
    )

    judge_dir = ctx.stage_path("04-judge")
    judge_dir.mkdir(parents=True, exist_ok=True)
    write_json(judge_dir / "verdict.json", verdict.model_dump(mode="json"))
    if gaps:
        (judge_dir / "gaps.md").write_text("\n".join(f"- {gap}" for gap in gaps) + "\n", encoding="utf-8")
    return verdict
