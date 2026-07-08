# Research methodology

Dev Scout exists to **research and scout** practical improvements for software development: speed, robustness, and production readiness.

## Jam

A finding is only promoted if it is **jam**:

- Primary **source link**
- **How-to steps** (3–7 concrete steps)
- **Evidence** (metric, benchmark, named outcome)
- Benefit: `speed`, `robustness`, or `both`

See `config/jam-criteria.yaml` and `system/memory/evidence-rubric.yaml`.

## Weekly flow

1. Set research questions in `GOAL.md`
2. Discover sources from playbook + `config/sources.yaml`
3. Collect and extract excerpts
4. Run lenses (`config/lenses/`)
5. Corroborate claims
6. Judge sufficiency
7. If pass → digest + email; if fail → feedback and re-research

## Research memory

- `data/findings.json` — cross-week ledger (dedupe)
- `system/memory/discovery-playbook.yaml` — how to search
- Prior `runs/` — audit trail
