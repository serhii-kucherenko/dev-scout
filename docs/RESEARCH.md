# Research methodology

Dev Scout is a **chat-driven harness**. The Cursor agent researches the web and writes files — no CLI.

## Jam

A finding is only promoted if it is **jam**:

- Primary **source link**
- **How-to steps** (3–7 concrete steps)
- **Evidence** (metric, benchmark, named outcome)
- Benefit: `speed`, `robustness`, or `both`

See `config/jam-criteria.yaml`, `templates/jam-item.example.json`, and `system/memory/evidence-rubric.yaml`.

## Weekly flow (in chat)

1. User kickoff → agent reads [CHAT-LOOP.md](CHAT-LOOP.md)
2. Discover sources from playbook + `config/sources.yaml`
3. Collect excerpts → `01-research/excerpts.jsonl`
4. Run lenses → `01-research/lenses/<id>/output.json`
5. Corroborate → `01-research/corroboration.json`
6. Judge → `04-judge/verdict.json`
7. If pass → digest + email; if fail → feedback and re-research

## Research memory

- `data/findings.json` — cross-week ledger (dedupe)
- `system/memory/discovery-playbook.yaml` — how to search
- Prior `runs/` — audit trail
