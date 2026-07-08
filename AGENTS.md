# Dev Scout — Agent Instructions

Research-first harness. Read in this order:

1. [docs/RESEARCH.md](docs/RESEARCH.md)
2. `runs/YYYY-Www/GOAL.md`
3. [docs/DISCOVERY-PLAYBOOK.md](docs/DISCOVERY-PLAYBOOK.md)
4. `runs/YYYY-Www/RUN.md`

## Rules

- **Research before output.** Run `discover → collect → lens → corroborate → coverage → judge` before `report` or `compose-email`.
- **Jam criteria.** Every promoted item needs `source_url`, `how_to_steps` (≥3), and evidence grade A or B.
- **No fluff.** Skip meta advice, listicles without links, hype without how-to.
- **Gap feedback.** If judge fails, write `feedback-NNN.md` with specific missing sources/lenses — then re-run discovery scoped to gaps.

## Stage commands

```bash
dev-scout discover|collect|lens --all|corroborate|coverage|judge --json
dev-scout week --week 2026-W28
dev-scout loop --goal-file runs/2026-W28/GOAL.md
dev-scout report|compose-email|send   # only after judge sufficient
```

## Discovery backends

Use per [docs/DISCOVERY-PLAYBOOK.md](docs/DISCOVERY-PLAYBOOK.md):

- Exa / Brave for web search
- agent-reach for discussion corroboration
- `gh search` for repos
- Direct fetch for primary sources

## Output

- `01-research/` — auditable research trail
- `05-report/weekly-digest.md` — full jam cookbook
- `06-email/email-draft.md` — scannable weekly brief
