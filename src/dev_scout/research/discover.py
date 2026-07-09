from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dev_scout.context import RunContext
from dev_scout.util import config_dir, data_dir, load_yaml, read_json, system_memory_dir, write_json


def _seed_urls_from_ledger() -> list[dict[str, Any]]:
    ledger = read_json(data_dir() / "findings.json")
    urls: list[dict[str, Any]] = []
    for item in ledger.get("findings", [])[-10:]:
        url = item.get("source_url")
        if url:
            urls.append({"url": url, "tier": "secondary", "reason": "prior_jam"})
    return urls


def _urls_from_sources() -> list[dict[str, Any]]:
    sources = load_yaml(config_dir() / "sources.yaml")
    playbook = load_yaml(system_memory_dir() / "discovery-playbook.yaml")
    entries: list[dict[str, Any]] = []

    for seed_group, queries in (sources.get("search_seeds") or {}).items():
        template = (playbook.get("lens_search_templates") or {}).get(seed_group, "{query}")
        for query in queries:
            entries.append(
                {
                    "url": f"search://{seed_group}/{query}",
                    "tier": "secondary",
                    "reason": "search_seed",
                    "lens_id": seed_group,
                    "query": template.format(query=query),
                }
            )

    for query in sources.get("github_queries") or []:
        entries.append(
            {
                "url": f"github-search://{query}",
                "tier": "primary",
                "reason": "github_query",
                "query": query,
            }
        )

    return entries


def _fixture_urls(use_fixtures: bool) -> list[dict[str, Any]]:
    if not use_fixtures:
        return []
    fixture_path = RunContext.fixture_root() / "discover_urls.json"
    if not fixture_path.exists():
        return []
    payload = read_json(fixture_path)
    return payload.get("urls", [])


def run_discover(ctx: RunContext, *, use_fixtures: bool = False) -> dict[str, Any]:
    ctx.ensure_layout()
    discover_dir = ctx.research_path("discover")
    discover_dir.mkdir(parents=True, exist_ok=True)

    urls = _fixture_urls(use_fixtures) or _urls_from_sources()
    urls.extend(_seed_urls_from_ledger())

    boundaries = load_yaml(config_dir() / "governance" / "data-boundaries.yaml")
    max_urls = int(boundaries.get("max_urls_per_run", 40))
    urls = urls[:max_urls]

    source_discovery = {
        "day": ctx.day,
        "url_count": len(urls),
        "urls": urls,
    }
    fetch_plan = {
        "day": ctx.day,
        "planned": len(urls),
        "entries": urls,
    }

    write_json(discover_dir / "source-discovery.json", source_discovery)
    write_json(discover_dir / "fetch-plan.json", fetch_plan)
    return {"planned": len(urls), "discover_dir": str(discover_dir)}


def host_allowed(url: str, boundaries: dict[str, Any]) -> bool:
    if url.startswith("search://") or url.startswith("github-search://"):
        return True
    host = urlparse(url).netloc.lower().removeprefix("www.")
    allowed = boundaries.get("allowed_hosts") or []
    return any(host == item or host.endswith("." + item) for item in allowed)
