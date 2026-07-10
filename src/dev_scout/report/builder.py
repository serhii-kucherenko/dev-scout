from __future__ import annotations

from dev_scout.compose.email import resolve_repo_url
from dev_scout.context import RunContext
from dev_scout.models.jam import JamItem, Track
from dev_scout.util import config_dir, load_yaml, read_json, write_json


def _track_config() -> dict:
    return load_yaml(config_dir() / "tracks.yaml").get("tracks", {})


def _track_order() -> list[Track]:
    return [Track.AI_DEVELOPMENT, Track.AI_DRIVEN_DEVELOPMENT]


def _track_label(track: Track) -> str:
    meta = _track_config().get(track.value, {})
    return str(meta.get("label") or track.value)


def _track_digest_intro(track: Track) -> str:
    meta = _track_config().get(track.value, {})
    return str(meta.get("digest_intro") or "")


def _group_by_track(items: list[JamItem]) -> list[tuple[Track, list[JamItem]]]:
    buckets: dict[Track, list[JamItem]] = {track: [] for track in _track_order()}
    for item in items:
        buckets.setdefault(item.track, []).append(item)
    return [(track, buckets[track]) for track in _track_order() if buckets[track]]


def _format_item(item: JamItem) -> str:
    steps = "\n".join(f"  {index}. {step}" for index, step in enumerate(item.how_to_steps, start=1))
    how_to = item.how_to_url or item.source_url
    return (
        f"### {item.title}\n\n"
        f"**Why:** {item.why}\n\n"
        f"**Benefit:** {item.benefit.value} | **Setup:** {item.setup_cost.value} | **Grade:** {item.evidence_grade.value}\n\n"
        f"**Evidence:** {item.evidence}\n\n"
        f"**Source:** {item.source_url}\n\n"
        f"**How-to:** {how_to}\n\n"
        f"**Steps:**\n{steps}\n\n"
        f"**Try today:** {item.try_today}\n"
    )


def run_report(ctx: RunContext) -> str:
    ranked = read_json(ctx.stage_path("03-rank") / "ranked.json")
    raw_items = ranked.get("items") or ranked.get("ranked") or []
    if raw_items and "how_to_steps" not in raw_items[0]:
        # Fall back to lens outputs when ranked.json only has summary rows.
        items: list[JamItem] = []
        lens_root = ctx.research_path("lenses")
        if lens_root.exists():
            for lens_dir in sorted(lens_root.iterdir()):
                output = lens_dir / "output.json"
                if output.exists():
                    payload = read_json(output)
                    items.extend(JamItem.model_validate(raw) for raw in payload.get("items", []))
    else:
        items = [JamItem.model_validate(raw) for raw in raw_items]
    promotable = [item for item in items if item.is_promotable()]

    lines = [
        f"# Dev Scout Daily Digest — {ctx.day}",
        "",
        "Actionable jam for faster, more robust development.",
        "",
    ]
    repo_url = resolve_repo_url()
    if repo_url:
        lines.extend([f"Repo: {repo_url}", ""])

    for track, track_items in _group_by_track(promotable):
        lines.extend([f"## {_track_label(track)}", ""])
        intro = _track_digest_intro(track)
        if intro:
            lines.extend([intro, ""])
        for item in track_items:
            lines.append(_format_item(item))
            lines.append("")

    lines.extend(["## All findings by lens", ""])
    by_lens: dict[str, list[JamItem]] = {}
    for item in promotable:
        by_lens.setdefault(item.lens_id, []).append(item)
    for lens_id, lens_items in sorted(by_lens.items()):
        lines.append(f"### {lens_id}")
        for item in lens_items:
            lines.append(f"- [{item.title}]({item.source_url}) ({item.track.value})")
        lines.append("")

    verdict = read_json(ctx.stage_path("04-judge") / "verdict.json")
    skipped = verdict.get("skipped") or []
    if skipped:
        lines.extend(["## Skipped", ""])
        lines.extend(f"- {line}" for line in skipped)
        lines.append("")

    content = "\n".join(lines)
    report_dir = ctx.stage_path("05-report")
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "daily-digest.md"
    path.write_text(content, encoding="utf-8")
    return str(path)
