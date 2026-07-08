# Dev Scout

[![CI](https://github.com/serhii-kucherenko/dev-scout/actions/workflows/ci.yml/badge.svg)](https://github.com/serhii-kucherenko/dev-scout/actions/workflows/ci.yml)

Weekly **chat-driven** research harness: open in Cursor, run the loop in chat, get **real jam** — source links, how-tos, and setup steps for faster, more robust AI-assisted development.

**No CLI. No API keys.** Uses your Cursor subscription only. See [docs/SUBSCRIPTIONS.md](docs/SUBSCRIPTIONS.md).

## How to use

1. **Open this repo in Cursor** as your project root
2. **Start a chat** and paste:

```
Run this week's dev scout research loop.
Read AGENTS.md and docs/CHAT-LOOP.md first.
Find practical ways to ship faster and build more robust software with AI-assisted dev.
Deliver jam with source links and how-tos when judge passes.
```

3. The agent researches the web, writes artifacts under `runs/YYYY-Www/`, and points you to the email draft when done

**Continue later:**

```
Continue the dev scout loop for runs/YYYY-Www/. Read RUN.md and pick up where we left off.
```

## What you get

| File | What it is |
|------|------------|
| `runs/YYYY-Www/06-email/email-draft.md` | Scannable weekly brief — start here |
| `runs/YYYY-Www/05-report/weekly-digest.md` | Full cookbook with all links and steps |
| `runs/YYYY-Www/01-research/` | Auditable research trail |

## Mission

Learn new practical workflows each week: agent harnesses, tooling setups, testing patterns, production practices that move real metrics. **Research is the core** — email and digest are outputs, not the product.

## Repo layout

```
AGENTS.md           ← agent entry (Cursor reads this)
docs/CHAT-LOOP.md   ← stage-by-stage chat loop
docs/SUBSCRIPTIONS.md ← no API keys; Cursor + agent-reach only
templates/          ← GOAL, feedback, jam examples
config/             ← lenses, judge rules, sources
runs/YYYY-Www/      ← weekly artifacts
data/findings.json  ← cross-week memory
src/dev_scout/      ← CI helpers only (optional)
```

## For agents

Everything runs in chat. See [AGENTS.md](AGENTS.md) and [docs/CHAT-LOOP.md](docs/CHAT-LOOP.md).

Never write digest or email until judge criteria in `config/judge.yaml` pass.

## License

MIT — see [LICENSE](LICENSE).
