# Collection

1. **Discover** writes `01-research/discover/fetch-plan.json`
2. **Collect** fetches each URL → `raw/`, `extracted/`, `excerpts.jsonl`

Allowed hosts: `config/governance/data-boundaries.yaml`.

Each excerpt record:

```json
{"url": "...", "title": "...", "text": "...", "lens_id": "...", "tier": "primary"}
```

Manual excerpts: append to `excerpts.jsonl` (document in `RUN.md`).
