from __future__ import annotations

from dev_scout import context as context_module
from dev_scout.compose import email as email_module
from dev_scout.context import RunContext
from dev_scout.learning import ledger as ledger_module
from dev_scout.judge.engine import run_judge
from dev_scout.models.jam import Benefit, EvidenceGrade, JamItem, SetupCost
from dev_scout.models.jam import current_run_day
from dev_scout.rank import score as score_module
from dev_scout.pipeline.day import run_day
from dev_scout.research import discover as discover_module
from dev_scout.research.corroborate import run_corroborate
from dev_scout.research.lenses import analyze_excerpt
from dev_scout.util import read_json, write_json


def _configure_tmp_paths(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    data = tmp_path / "data"
    monkeypatch.setattr(
        RunContext,
        "from_day",
        staticmethod(lambda day=None: RunContext(day=day or current_run_day(), root=runs)),
    )
    monkeypatch.setattr(context_module, "runs_dir", lambda: runs)
    monkeypatch.setattr(discover_module, "data_dir", lambda: data)
    monkeypatch.setattr(score_module, "data_dir", lambda: data)
    monkeypatch.setattr(ledger_module, "data_dir", lambda: data)
    monkeypatch.setattr(email_module, "data_dir", lambda: data)
    monkeypatch.setattr(email_module, "runs_dir", lambda: runs)
    write_json(data / "findings.json", {"findings": [], "days": []})
    return runs, data


def _write_lens_output(ctx: RunContext, lens_id: str, items: list[JamItem]) -> None:
    write_json(
        ctx.research_path("lenses", lens_id, "output.json"),
        {"lens_id": lens_id, "items": [item.model_dump(mode="json") for item in items]},
    )


def test_day_with_fixtures_produces_email(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    monkeypatch.setenv("DEV_SCOUT_EMAIL", "scout@example.com")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("DELIVERY_FROM", raising=False)

    result = run_day("2099-01-01", use_fixtures=True)
    assert result.verdict.sufficient
    assert result.email_path is not None
    assert result.digest_path is not None
    assert result.send_status == "skipped"
    email_dir = runs / "2099-01-01" / "06-email"
    manifest = read_json(runs / "2099-01-01" / "run.manifest.json")
    draft = read_json(email_dir / "email-draft.json")
    send_result = read_json(email_dir / "send-result.json")
    eml_text = (email_dir / "email-draft.eml").read_text(encoding="utf-8")

    assert (email_dir / "email-draft.md").exists()
    assert (email_dir / "email-draft.json").exists()
    assert (email_dir / "email-draft.eml").exists()
    assert draft["to"] == "scout@example.com"
    assert draft["to"] == manifest["email_to"]
    assert draft["subject"] == manifest["email_subject"]
    assert manifest["email_draft_path"] == "runs/2099-01-01/06-email/email-draft.md"
    assert manifest["email_json_path"] == "runs/2099-01-01/06-email/email-draft.json"
    assert manifest["email_eml_path"] == "runs/2099-01-01/06-email/email-draft.eml"
    assert manifest["digest_path"] == "runs/2099-01-01/05-report/daily-digest.md"
    assert manifest["send_status"] == "skipped"
    assert send_result["status"] == "skipped"
    assert send_result["to"] == "scout@example.com"
    assert eml_text.startswith(f"To: {draft['to']}\nSubject: {draft['subject']}\n")
    body = draft["body_text"]
    assert "Mission: practical ways to ship faster" in body
    assert "Previous email: none yet" in body
    assert "New jam today:" in body
    assert "Evidence:" in body
    assert "grade " in body
    assert "Setup cost:" in body
    assert "Corroboration:" in body
    assert "Lens:" in body
    assert "Source:" in body
    assert "How-to:" in body
    assert "Steps:" in body
    assert "Try today:" in body
    assert "Full digest: runs/2099-01-01/05-report/daily-digest.md" in body
    assert draft["new_count"] == len(draft["top_items"]) > 0
    ranked = read_json(runs / "2099-01-01" / "03-rank" / "ranked.json")
    assert all(
        not item["source_url"].startswith("https://example.com/dev-scout")
        for item in ranked["items"]
    )
    assert (runs / "2099-01-01" / "05-report" / "daily-digest.md").exists()
    assert (runs / "2099-01-01" / "07-learning" / "delta-vs-last-day.json").exists()


def test_followup_email_reviews_previous_and_skips_repeats(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    monkeypatch.setenv("DEV_SCOUT_EMAIL", "scout@example.com")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("DELIVERY_FROM", raising=False)

    first = run_day("2099-01-01", use_fixtures=True)
    assert first.verdict.sufficient
    first_draft = read_json(runs / "2099-01-01" / "06-email" / "email-draft.json")
    assert first_draft["top_items"]
    first_titles = {item["title"] for item in first_draft["top_items"]}

    second = run_day("2099-01-02", use_fixtures=True)
    assert second.verdict.sufficient
    second_draft = read_json(runs / "2099-01-02" / "06-email" / "email-draft.json")
    body = second_draft["body_text"]

    assert second_draft["previous_day"] == "2099-01-01"
    assert "Quick review of previous email (2099-01-01):" in body
    for title in list(first_titles)[:3]:
        assert f"- {title}" in body
    assert "No new jam today." in body
    assert "Nothing new beyond what we already covered" in body
    assert second_draft["top_items"] == []
    assert second_draft["new_count"] == 0
    assert second_draft["subject"] == "Dev Scout 2099-01-02 — no new jam"


def test_followup_email_includes_only_unseen_findings(tmp_path, monkeypatch):
    from dev_scout.compose.email import run_compose_email
    from dev_scout.models.jam import CorroborationStatus

    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    monkeypatch.setenv("DEV_SCOUT_EMAIL", "scout@example.com")

    prior_ctx = RunContext("2099-01-01", root=runs)
    prior_ctx.ensure_layout()
    write_json(
        prior_ctx.stage_path("06-email") / "email-draft.json",
        {
            "subject": "Dev Scout 2099-01-01 — 1 new ways to ship faster / build safer",
            "to": "scout@example.com",
            "body_text": "prior",
            "top_items": [
                {
                    "id": "old-1",
                    "title": "Already emailed finding",
                    "why": "Why",
                    "benefit": "speed",
                    "source_url": "https://example.com/already-sent",
                    "how_to_steps": ["a", "b", "c"],
                    "setup_cost": "hours",
                    "evidence": "2x PR velocity",
                    "evidence_grade": "A",
                    "lens_id": "ship-faster",
                    "corroboration": "supported",
                    "try_today": "Reuse yesterday",
                }
            ],
            "new_count": 1,
        },
    )

    ctx = RunContext("2099-01-02", root=runs)
    ctx.ensure_layout()
    write_json(
        ctx.stage_path("03-rank") / "ranked.json",
        {
            "day": "2099-01-02",
            "items": [
                {
                    "id": "old-1",
                    "title": "Already emailed finding",
                    "why": "Why",
                    "benefit": "speed",
                    "source_url": "https://example.com/already-sent",
                    "how_to_steps": ["a", "b", "c"],
                    "setup_cost": "hours",
                    "evidence": "2x PR velocity",
                    "evidence_grade": "A",
                    "lens_id": "ship-faster",
                    "corroboration": CorroborationStatus.SUPPORTED.value,
                    "try_today": "Reuse yesterday",
                },
                {
                    "id": "new-1",
                    "title": "Brand new finding",
                    "why": "Fresh why",
                    "benefit": "robustness",
                    "source_url": "https://example.com/brand-new",
                    "how_to_steps": ["Clone", "Configure", "Verify"],
                    "setup_cost": "minutes",
                    "evidence": "fewer escaped bugs",
                    "evidence_grade": "A",
                    "lens_id": "build-robust",
                    "corroboration": CorroborationStatus.SUPPORTED.value,
                    "try_today": "Try the new path",
                },
            ],
        },
    )

    draft = run_compose_email(ctx)
    assert [item.title for item in draft.top_items] == ["Brand new finding"]
    assert "Already emailed finding" in draft.body_text
    assert "Quick review of previous email (2099-01-01):" in draft.body_text
    assert "Brand new finding" in draft.body_text
    assert "https://example.com/brand-new" in draft.body_text
    assert "No new jam today." not in draft.body_text


def test_day_sends_findings_email_when_resend_configured(tmp_path, monkeypatch):
    runs, _ = _configure_tmp_paths(tmp_path, monkeypatch)
    monkeypatch.setenv("DEV_SCOUT_EMAIL", "scout@example.com")
    monkeypatch.setenv("RESEND_API_KEY", "re_test_key")
    monkeypatch.setenv("DELIVERY_FROM", "Dev Scout <onboarding@resend.dev>")

    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, str]:
            return {"id": "email_123"}

    class _FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def post(self, url, headers=None, json=None):
            assert url == "https://api.resend.com/emails"
            assert headers["Authorization"] == "Bearer re_test_key"
            assert json["to"] == ["scout@example.com"]
            assert json["from"] == "Dev Scout <onboarding@resend.dev>"
            assert "Dev Scout — 2099-01-01" in json["text"]
            assert "Evidence:" in json["text"]
            assert "Try today:" in json["text"]
            assert "Source:" in json["text"]
            assert "Steps:" in json["text"]
            return _FakeResponse()

    monkeypatch.setattr("dev_scout.delivery.send.httpx.Client", _FakeClient)

    result = run_day("2099-01-01", use_fixtures=True)
    assert result.send_status == "sent"
    assert result.send_result["id"] == "email_123"
    assert result.send_result["to"] == "scout@example.com"
    send_result = read_json(runs / "2099-01-01" / "06-email" / "send-result.json")
    assert send_result["status"] == "sent"
    assert send_result["id"] == "email_123"


def test_resolve_recipient_prefers_env(monkeypatch):
    from dev_scout.compose.email import resolve_recipient

    monkeypatch.delenv("DEV_SCOUT_EMAIL", raising=False)
    monkeypatch.delenv("DELIVERY_TO", raising=False)
    assert resolve_recipient({"recipient": "fallback@example.com"}) == "fallback@example.com"

    monkeypatch.setenv("DELIVERY_TO", "alias@example.com")
    assert resolve_recipient({"recipient": "fallback@example.com"}) == "alias@example.com"

    monkeypatch.setenv("DEV_SCOUT_EMAIL", "primary@example.com")
    assert resolve_recipient({"recipient": "fallback@example.com"}) == "primary@example.com"


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


def test_jam_item_accepts_legacy_try_monday():
    item = JamItem.model_validate(
        {
            "id": "legacy-1",
            "title": "Legacy",
            "why": "Why",
            "benefit": "speed",
            "source_url": "https://example.com/legacy",
            "how_to_steps": ["a", "b", "c"],
            "setup_cost": "hours",
            "evidence": "2x PR velocity",
            "evidence_grade": "A",
            "lens_id": "ship-faster",
            "try_monday": "Try this today",
        }
    )
    assert item.try_today == "Try this today"


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
    ctx = RunContext("2099-01-02", root=runs)
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
    ctx = RunContext("2099-01-05", root=runs)
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
    ctx = RunContext("2099-01-03", root=runs)
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
    ctx = RunContext("2099-01-06", root=runs)
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
    ctx = RunContext("2099-01-04", root=runs)
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
    write_json(ctx.stage_path("03-rank") / "ranked.json", {"day": ctx.day, "items": []})

    verdict = run_judge(ctx)

    assert verdict.promoted_count == 1
    ranked = read_json(ctx.stage_path("03-rank") / "ranked.json")
    assert ranked["items"][0]["id"] == item.id
