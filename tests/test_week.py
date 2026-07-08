from __future__ import annotations

from dev_scout.models.jam import Benefit, EvidenceGrade, JamItem, SetupCost
from dev_scout.pipeline.week import run_week


def test_week_with_fixtures_produces_email(tmp_path, monkeypatch):
    monkeypatch.setenv("DEV_SCOUT_RUNS_DIR", str(tmp_path / "runs"))
    from dev_scout import context as context_module

    monkeypatch.setattr(context_module, "runs_dir", lambda: tmp_path / "runs")

    result = run_week("2099-W01", use_fixtures=True)
    assert result.verdict.sufficient
    assert result.email_path is not None
    assert result.digest_path is not None


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
