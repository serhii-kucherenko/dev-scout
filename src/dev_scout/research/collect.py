from __future__ import annotations

import hashlib
import re
from typing import Any

import httpx

from dev_scout.context import RunContext
from dev_scout.research.discover import host_allowed
from dev_scout.util import append_jsonl, config_dir, load_yaml, read_json, write_json


def _slug(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def _extract_text(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _fetch_url(url: str, timeout: float) -> str:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": "dev-scout/0.1"})
        response.raise_for_status()
        return response.text


def _load_fixture_excerpts(use_fixtures: bool) -> list[dict[str, Any]]:
    if not use_fixtures:
        return []
    path = RunContext.fixture_root() / "excerpts.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(__import__("json").loads(line))
    return rows


def run_collect(ctx: RunContext, *, use_fixtures: bool = False) -> dict[str, Any]:
    ctx.ensure_layout()
    fetch_plan = read_json(ctx.research_path("discover", "fetch-plan.json"))
    boundaries = load_yaml(config_dir() / "governance" / "data-boundaries.yaml")
    timeout = float(boundaries.get("request_timeout_seconds", 30))

    raw_dir = ctx.research_path("raw")
    extracted_dir = ctx.research_path("extracted")
    excerpts_path = ctx.research_path("excerpts.jsonl")
    if excerpts_path.exists():
        excerpts_path.unlink()

    fetched = 0
    extracted = 0

    if use_fixtures:
        for row in _load_fixture_excerpts(use_fixtures=True):
            append_jsonl(excerpts_path, row)
            extracted += 1
        result = {"fetched": fetched, "extracted": extracted, "excerpts": str(excerpts_path)}
        write_json(ctx.research_path("collect-summary.json"), result)
        return result

    for entry in fetch_plan.get("entries", []):
        url = entry.get("url", "")
        if not url or not host_allowed(url, boundaries):
            continue
        if url.startswith("search://") or url.startswith("github-search://"):
            append_jsonl(
                excerpts_path,
                {
                    "url": url,
                    "title": entry.get("query", url),
                    "text": entry.get("query", ""),
                    "lens_id": entry.get("lens_id"),
                    "tier": entry.get("tier", "secondary"),
                },
            )
            extracted += 1
            continue
        try:
            html = _fetch_url(url, timeout)
            slug = _slug(url)
            (raw_dir / f"{slug}.html").write_text(html, encoding="utf-8")
            text = _extract_text(html)
            (extracted_dir / f"{slug}.txt").write_text(text, encoding="utf-8")
            append_jsonl(
                excerpts_path,
                {
                    "url": url,
                    "title": text[:120],
                    "text": text[:4000],
                    "lens_id": entry.get("lens_id"),
                    "tier": entry.get("tier", "secondary"),
                },
            )
            fetched += 1
            extracted += 1
        except httpx.HTTPError:
            continue

    result = {"fetched": fetched, "extracted": extracted, "excerpts": str(excerpts_path)}
    write_json(ctx.research_path("collect-summary.json"), result)
    return result
