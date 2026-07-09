from __future__ import annotations

from dev_scout import context as context_module
from dev_scout.context import RunContext
from dev_scout.learning import ledger as ledger_module
from dev_scout.judge.engine import run_judge
from dev_scout.models.jam import Benefit, EvidenceGrade, JamItem, SetupCost
from dev_scout.models.jam import current_iso_week
from dev_scout.rank import score as score_module
from dev_scout.pipeline import week as week_module
from dev_scout.pipeline.week import run_week
from dev_scout.research import discover as discover_module
from dev_scout.research.corroborate import run_corroborate
from dev_scout.research.lenses import analyze_excerpt
from dev_scout.util import read_json, write_json


def _configure_tmp_paths(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    data = tmp_path / "data"
    monkeypatch.setattr(
        RunContext,
        "from_week",
        staticmethod(lambda week=None: RunContext(week=week or current_iso_week(), root=runs)),
    )
    monkeypatch.setattr(context_module, "runs_dir", lambda: runs)
    monkeypatch.setattr(discover_module, "data_dir", lambda: data)
    monkeypatch.setattr(score_module, "data_dir", lambda: data)
    monkeypatch.setattr(ledger_module, "data_dir", lambda: data)
    write_json(data / "findings.json", {"findings": [], "weeks": []})
    return runs, data


def _write_lens_output(ctx: RunContext, lens_id: str, items: list[JamItem]) -> None:
    write_json(
        ctx.research_path("lenses", lens_id, "output.json"),
        {"lens_id": lens_id, "items": [item.model_dump(mode="json") for item in items]},
    )


def test_week_with_fixtures_produces_email(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)

    result = run_week("2099-W01", use_fixtures=True)
    assert result.verdict.sufficient
    assert result.email_path is not None
    assert result.digest_path is not None
    ranked = read_json(runs / "2099-W01" / "03-rank" / "ranked.json")
    assert all(
        not item["source_url"].startswith("https://example.com/dev-scout")
        for item in ranked["items"]
    )


def test_jam_item_promotable():
    item = JamItem(
        id="test-1",
        title="Test",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://example.com/a",
        how_to_steps=["a", "b", "c"],
        setup_cost=SetupCost.MINUTES,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="ship-faster",
    )
    assert item.is_promotable()


def test_jam_item_rejects_placeholder_steps():
    item = JamItem(
        id="test-template",
        title="Test",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://example.com/template",
        how_to_steps=[
            "Open the source: https://example.com/template",
            "Skim for prerequisites and install commands",
            "Apply the workflow on a small branch before team rollout",
            "Measure cycle time or defect rate for one week",
        ],
        setup_cost=SetupCost.HOURS,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="ship-faster",
    )
    assert not item.is_promotable()


def test_jam_item_rejects_low_grade():
    item = JamItem(
        id="test-2",
        title="Test",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://example.com/b",
        how_to_steps=["a", "b", "c"],
        setup_cost=SetupCost.HOURS,
        evidence="weak",
        evidence_grade=EvidenceGrade.D,
        lens_id="ship-faster",
    )
    assert not item.is_promotable()


def test_analyze_excerpt_skips_search_only_sources():
    excerpt = {
        "url": "search://ship-faster/agent loop benchmark",
        "title": "Agent loop benchmark",
        "text": "Agent loop benchmark with 2x faster reviews. 1. Clone repo 2. Run agent loop 3. Compare review counts",
        "lens_id": "ship-faster",
        "tier": "secondary",
    }
    lens_cfg = {
        "keywords": ["agent loop", "reviews"],
        "benefit": "speed",
        "question": "What agent loops improve review speed?",
        "required_evidence": "time saved",
    }
    assert analyze_excerpt(excerpt, "ship-faster", lens_cfg, 1) is None


def test_corroborate_requires_independent_source(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    ctx = RunContext("2099-W02", root=runs)
    ctx.ensure_layout()
    item = JamItem(
        id="ship-faster-1",
        title="Ralph loop agent harness",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://github.com/vercel-labs/ralph-loop-agent",
        how_to_steps=["Clone repo", "Configure verify step", "Run loop on a branch"],
        setup_cost=SetupCost.HOURS,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="ship-faster",
    )
    _write_lens_output(ctx, "ship-faster", [item])
    ctx.research_path("excerpts.jsonl").write_text("", encoding="utf-8")
    results = run_corroborate(ctx)
    assert results[item.id] == "weak"


def test_corroborate_ignores_same_source_url_variants(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    ctx = RunContext("2099-W05", root=runs)
    ctx.ensure_layout()
    item = JamItem(
        id="ship-faster-1",
        title="Ralph loop agent harness",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://github.com/vercel-labs/ralph-loop-agent",
        how_to_steps=["Clone repo", "Configure verify step", "Run loop on a branch"],
        setup_cost=SetupCost.HOURS,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="ship-faster",
    )
    _write_lens_output(ctx, "ship-faster", [item])
    ctx.research_path("excerpts.jsonl").write_text(
        '{"url": "https://github.com/vercel-labs/ralph-loop-agent/", "title": "Ralph loop agent harness mirror", "text": "Ralph loop agent harness notes repeat the same agent loop gains"}\n',
        encoding="utf-8",
    )

    results = run_corroborate(ctx)

    assert results[item.id] == "weak"


def test_rank_dedupes_duplicate_sources(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    ctx = RunContext("2099-W03", root=runs)
    ctx.ensure_layout()
    primary = JamItem(
        id="ship-faster-1",
        title="Ralph loop agent harness",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://github.com/vercel-labs/ralph-loop-agent",
        how_to_steps=["Clone repo", "Configure verify step", "Run loop on a branch"],
        setup_cost=SetupCost.HOURS,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="ship-faster",
    )
    duplicate = JamItem(
        id="tooling-setups-1",
        title="Ralph loop agent harness for setup",
        why="Why",
        benefit=Benefit.BOTH,
        source_url="https://github.com/vercel-labs/ralph-loop-agent",
        how_to_steps=["Clone repo", "Configure verify step", "Run loop on a branch"],
        setup_cost=SetupCost.HOURS,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="tooling-setups",
    )
    _write_lens_output(ctx, "ship-faster", [primary])
    _write_lens_output(ctx, "tooling-setups", [duplicate])

    ranked = score_module.run_rank(ctx)
    assert len(ranked) == 1
    assert ranked[0].source_url == primary.source_url


def test_rank_keeps_distinct_query_identified_sources(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    ctx = RunContext("2099-W06", root=runs)
    ctx.ensure_layout()
    first = JamItem(
        id="ship-faster-1",
        title="First HN discussion",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://news.ycombinator.com/item?id=1",
        how_to_steps=["Open thread", "Review examples", "Test on a branch"],
        setup_cost=SetupCost.HOURS,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="ship-faster",
    )
    second = JamItem(
        id="ship-faster-2",
        title="Second HN discussion",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://news.ycombinator.com/item?id=2",
        how_to_steps=["Open thread", "Review examples", "Test on a branch"],
        setup_cost=SetupCost.HOURS,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="ship-faster",
    )
    _write_lens_output(ctx, "ship-faster", [first, second])

    ranked = score_module.run_rank(ctx)

    assert len(ranked) == 2
    assert {item.source_url for item in ranked} == {first.source_url, second.source_url}


def test_judge_rebuilds_stale_ranked_output(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    ctx = RunContext("2099-W04", root=runs)
    ctx.ensure_layout()
    item = JamItem(
        id="ship-faster-1",
        title="Fresh finding",
        why="Why",
        benefit=Benefit.SPEED,
        source_url="https://example.com/fresh",
        how_to_steps=["Clone repo", "Configure verify step", "Run loop on a branch"],
        setup_cost=SetupCost.HOURS,
        evidence="2x PR velocity",
        evidence_grade=EvidenceGrade.A,
        lens_id="ship-faster",
    )
    _write_lens_output(ctx, "ship-faster", [item])
    write_json(ctx.research_path("corroboration.json"), {})
    write_json(ctx.stage_path("03-rank") / "ranked.json", {"week": ctx.week, "items": []})

    verdict = run_judge(ctx)

    assert verdict.promoted_count == 1
    ranked = read_json(ctx.stage_path("03-rank") / "ranked.json")
    assert ranked["items"][0]["id"] == item.id
