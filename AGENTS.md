# Dev Scout — Cursor agent instructions

**This is a chat-driven harness.** The user opens this repo in Cursor and runs the research loop in chat. You write files under `runs/YYYY-MM-DD/`. Do not ask the user to run a CLI.

## Read first

1. [docs/CHAT-LOOP.md](docs/CHAT-LOOP.md) — stage-by-stage loop
2. [docs/SUBSCRIPTIONS.md](docs/SUBSCRIPTIONS.md) — no API keys; use Cursor + agent-reach
3. [docs/RESEARCH.md](docs/RESEARCH.md) — mission and jam criteria
4. [docs/DISCOVERY-PLAYBOOK.md](docs/DISCOVERY-PLAYBOOK.md) — how to search
5. `runs/YYYY-MM-DD/GOAL.md` or copy from [templates/GOAL.md](templates/GOAL.md)
6. `runs/YYYY-MM-DD/RUN.md` if resuming

## Your job

**Research and scout** the web for ways to speed up development and make it more robust. Deliver **real jam**: source links, how-tos, setup steps.

## Loop (repeat until judge passes)

```
intake → discover → collect → lenses → corroborate → coverage → judge
  ↓ fail: write feedback-NNN.md, go back to discover (scoped)
  ↓ pass: synthesize → rank → report → email → learning
```

### Stage actions (all in chat + file writes)

| Stage | You do |
|-------|--------|
| **Discover** | Web search per playbook; write `01-research/discover/fetch-plan.json` |
| **Collect** | Fetch sources; append `01-research/excerpts.jsonl` |
| **Lenses** | For each lens in `config/lenses/`, write `01-research/lenses/<id>/output.json` |
| **Corroborate** | Find second sources; write `01-research/corroboration.json` |
| **Coverage** | Write `01-research/coverage.json` |
| **Judge** | Apply `config/judge.yaml`; write `04-judge/verdict.json` |
| **Output** | Write `03-rank/ranked.json`, `05-report/daily-digest.md`, `06-email/email-draft.*` addressed to `DEV_SCOUT_EMAIL` |
| **Send** | Email findings to `DEV_SCOUT_EMAIL` (review previous brief; only new jam; say so if none) |
| **Learn** | Update `data/findings.json`, write `07-learning/delta-vs-last-day.json` |

Update `RUN.md` after every stage.

After judge passes and drafts are written, **send the findings email** when secrets are available:

```bash
python -m dev_scout.cli send --day YYYY-MM-DD
```

(or the full `day` pipeline, which sends automatically). Record status in `06-email/send-result.json`.

## Jam rules (non-negotiable)

- Every promoted item: `source_url` + `how_to_steps` (≥3) + grade A or B
- Benefit must be `speed`, `robustness`, or `both`
- No meta fluff, listicles without links, hype without how-to
- See `config/jam-criteria.yaml` and `templates/jam-item.example.json`

## Discovery (subscriptions only — no LLM/search API keys)

Use only what the user already pays for for research. **Never ask for OpenAI, Anthropic, or Exa keys.**

Delivery of the findings email uses `DEV_SCOUT_EMAIL` + Resend (`RESEND_API_KEY`, `DELIVERY_FROM`) — see [docs/DELIVERY.md](docs/DELIVERY.md).

| Tool | Use |
|------|-----|
| **This Cursor chat** | Analysis, lenses, judge, writing outputs |
| **Cursor web search** | Discover sources |
| **agent-reach** | HN, Reddit, Twitter, GitHub, articles (use agent-reach skill when available) |
| **`gh search`** | GitHub repos/issues if `gh` is authenticated |
| **Web fetch** | Read primary sources |

Full details: [docs/DISCOVERY-PLAYBOOK.md](docs/DISCOVERY-PLAYBOOK.md) and [docs/SUBSCRIPTIONS.md](docs/SUBSCRIPTIONS.md).

Respect `config/governance/data-boundaries.yaml`.

## When judge fails

Write `feedback-NNN.md` from [templates/feedback.md](templates/feedback.md). Tell the user what's missing. Re-research. **Do not** write email until sufficient.

## When judge passes

Tell the user:

> Today's jam is ready: `runs/YYYY-MM-DD/06-email/email-draft.md`  
> Full detail: `runs/YYYY-MM-DD/05-report/daily-digest.md`  
> Sent to: `$DEV_SCOUT_EMAIL` (see `06-email/send-result.json`)

## Optional

`src/dev_scout/` is for CI only. Do not require `pip install`, terminal commands, or **any API keys** for the user.

## Cursor Cloud specific instructions

This section is for the optional Python harness in `src/dev_scout/` (CI helper only). The user-facing product is the chat loop above and needs none of this.

- **Dependencies live in a `.venv`.** System Python (3.12) is externally managed (Debian), so the startup update script installs the package with `[dev]` extras into `.venv`. Run tools via `. .venv/bin/activate` or call `.venv/bin/<tool>` directly. Reinstall deps with `.venv/bin/pip install -e ".[dev]"`.
- **No console-script entry point.** Run the CLI as a module: `python -m dev_scout.cli <command>` (e.g. `doctor`, `day`). `dev-scout` is not on `PATH`.
- **Tests / build:** `pytest -q` is the whole build+test (see `.github/workflows/ci.yml`). Lint (`ruff check .`) is available via the `[dev]` extras but is not run in CI and currently reports pre-existing findings.
- **Run offline with fixtures.** The pipeline needs no network or API keys when given `--fixtures`, e.g. `python -m dev_scout.cli day --day 2099-01-01 --fixtures`. It writes into `runs/<day>/` in the repo working tree (the `DEV_SCOUT_RUNS_DIR` env var is not honored by the CLI — only the test suite monkeypatches `runs_dir`). Use a throwaway day like `2099-01-01` and `git checkout -- runs/` afterward to avoid committing regenerated artifacts.
