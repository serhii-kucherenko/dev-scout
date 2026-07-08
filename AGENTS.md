# Dev Scout — Cursor agent instructions

**This is a chat-driven harness.** The user opens this repo in Cursor and runs the research loop in chat. You write files under `runs/YYYY-Www/`. Do not ask the user to run a CLI.

## Read first

1. [docs/CHAT-LOOP.md](docs/CHAT-LOOP.md) — stage-by-stage loop
2. [docs/SUBSCRIPTIONS.md](docs/SUBSCRIPTIONS.md) — no API keys; use Cursor + agent-reach
3. [docs/RESEARCH.md](docs/RESEARCH.md) — mission and jam criteria
4. [docs/DISCOVERY-PLAYBOOK.md](docs/DISCOVERY-PLAYBOOK.md) — how to search
5. `runs/YYYY-Www/GOAL.md` or copy from [templates/GOAL.md](templates/GOAL.md)
6. `runs/YYYY-Www/RUN.md` if resuming

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
| **Output** | Write `03-rank/ranked.json`, `05-report/weekly-digest.md`, `06-email/email-draft.md` |
| **Learn** | Update `data/findings.json`, write `07-learning/delta-vs-last-week.json` |

Update `RUN.md` after every stage.

## Jam rules (non-negotiable)

- Every promoted item: `source_url` + `how_to_steps` (≥3) + grade A or B
- Benefit must be `speed`, `robustness`, or `both`
- No meta fluff, listicles without links, hype without how-to
- See `config/jam-criteria.yaml` and `templates/jam-item.example.json`

## Discovery (subscriptions only — no API keys)

Use only what the user already pays for. **Never ask for OpenAI, Anthropic, Exa, or other API keys.**

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

> This week's jam is ready: `runs/YYYY-Www/06-email/email-draft.md`  
> Full detail: `runs/YYYY-Www/05-report/weekly-digest.md`

## Optional

`src/dev_scout/` is for CI only. Do not require `pip install`, terminal commands, or **any API keys** for the user.
