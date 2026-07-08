# Dev Scout

[![CI](https://github.com/serhii-kucherenko/dev-scout/actions/workflows/ci.yml/badge.svg)](https://github.com/serhii-kucherenko/dev-scout/actions/workflows/ci.yml)

Weekly research harness that scouts the web for better ways to **ship faster** and **build more robust** software with AI-assisted development — then delivers **real jam**: source links, how-tos, and setup steps.

Personal research tool. Not a newsletter generator.

## Mission

Learn new practical workflows each week: agent harnesses, tooling setups, testing patterns, and production practices that move real metrics. Research is the core; email and digest are how the jam reaches you.

## Quick start

```bash
cd ~/Projects/dev-scout
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # optional keys for search, LLM, email send

dev-scout doctor
dev-scout week --fixtures   # smoke run with fixture data
```

## Weekly workflow

```bash
dev-scout week                    # full pipeline for current ISO week
# Read runs/YYYY-Www/06-email/email-draft.md
# Full detail: runs/YYYY-Www/05-report/weekly-digest.md
dev-scout send --dry-run          # optional, when delivery.mode = send
```

## CLI reference

| Command | Layer | Purpose |
|---------|-------|---------|
| `discover` | Research | Build fetch plan from playbook + sources |
| `collect` | Research | Fetch sources, build excerpts |
| `lens --all` | Research | Run research lenses on excerpts |
| `corroborate` | Research | Grade claim support |
| `coverage` | Research | Research health report |
| `judge` | Research | Sufficiency + jam quality gate |
| `week` | Orchestrator | Full weekly run |
| `loop --goal-file GOAL.md` | Orchestrator | Re-research until sufficient |
| `report` | Output | Full weekly digest (after judge pass) |
| `compose-email` | Output | Email draft with top jam |
| `send` | Output | Deliver via Resend (optional) |

Add `--json` to any command for agent-friendly output.

## Repo layout

```
config/          lenses, sources, judge rules, delivery
system/memory/   discovery playbook, evidence rubric
docs/            research methodology + agent loop
runs/YYYY-Www/   weekly artifacts (research → digest → email)
data/            cross-week findings ledger
src/dev_scout/   Python package
```

## For agents

Start with [AGENTS.md](AGENTS.md) and [docs/RESEARCH.md](docs/RESEARCH.md). Never compose email until `judge` passes.

## License

MIT — see [LICENSE](LICENSE).
