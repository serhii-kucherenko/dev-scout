# Collection

Agent workflow in chat:

1. **Discover** — write `01-research/discover/fetch-plan.json` from web search results
2. **Collect** — fetch each URL, append to `01-research/excerpts.jsonl`

Allowed hosts: `config/governance/data-boundaries.yaml`.

Excerpt record format:

```json
{"url": "...", "title": "...", "text": "...", "lens_id": "...", "tier": "primary"}
```

Optional: save HTML in `01-research/raw/` (gitignored).

Manual excerpts: append to `excerpts.jsonl` and note in `RUN.md`.
