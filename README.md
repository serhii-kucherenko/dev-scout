# Dev Scout

[![CI](https://github.com/serhii-kucherenko/dev-scout/actions/workflows/ci.yml/badge.svg)](https://github.com/serhii-kucherenko/dev-scout/actions/workflows/ci.yml)

Daily **chat-driven** research harness: open in Cursor, run the loop in chat, get **real jam** — source links, how-tos, and setup steps for faster, more robust AI-assisted development.

**No CLI required. No LLM API keys.** Research runs through your Cursor subscription. See [docs/SUBSCRIPTIONS.md](docs/SUBSCRIPTIONS.md).

---

## Who this is for

- Developers who want a **daily brief** of practical AI-assisted dev workflows — not hype, not listicles
- Teams that want an **auditable research trail** (sources, excerpts, corroboration) under version control
- Anyone who already uses **Cursor** and wants a repeatable way to scout the web for ship-faster / build-safer patterns

You do not run a terminal pipeline. You open the repo in Cursor and drive research from chat.

---

## Prerequisites

| Required | Optional |
|----------|----------|
| [Cursor](https://cursor.com) (Pro or Business) | [Resend](https://resend.com) account for email delivery |
| Git | `gh auth login` for GitHub search during discovery |
| This repo cloned or forked | [agent-reach](https://github.com) skill in Cursor for HN/Reddit/Twitter |

**You do not need:** OpenAI, Anthropic, Exa, or other search API keys. See [docs/SUBSCRIPTIONS.md](docs/SUBSCRIPTIONS.md).

---

## Quick start (5 minutes)

### 1. Get the repo

```bash
git clone https://github.com/serhii-kucherenko/dev-scout.git
cd dev-scout
```

Or fork it to your GitHub account and clone your fork.

### 2. Open in Cursor

Open the repo root as your Cursor workspace. Cursor reads [AGENTS.md](AGENTS.md) and `.cursor/rules/` automatically.

### 3. Start a chat and paste this

```
Run today's dev scout research loop.
Read AGENTS.md and docs/CHAT-LOOP.md first.
Find practical ways to ship faster and build more robust software with AI-assisted dev.
Deliver jam with source links and how-tos when judge passes.
```

### 4. Read the output

When the loop finishes (judge passes), start here:

| File | What it is |
|------|------------|
| `runs/YYYY-MM-DD/06-email/email-draft.md` | Scannable daily brief — **start here** |
| `runs/YYYY-MM-DD/05-report/daily-digest.md` | Full cookbook with links, steps, and evidence |
| `runs/YYYY-MM-DD/01-research/` | Auditable research trail (sources, excerpts, lenses) |

The agent tells you the exact paths when done.

---

## What happens in a run

The agent follows a fixed loop. You do not need to manage stages yourself — just kick off chat and let it work. Artifacts land under `runs/YYYY-MM-DD/`.

```
intake → discover → collect → lenses → corroborate → coverage → judge
  ↓ fail: feedback + re-research (no email yet)
  ↓ pass: rank → report → email draft → learning
```

| Stage | What you get |
|-------|----------------|
| **Discover** | Web search plan and candidate sources |
| **Collect** | Fetched excerpts from primary sources |
| **Lenses** | Findings grouped by theme (ship faster, build robust, tooling, etc.) |
| **Judge** | Quality gate — only promoted items with links + how-tos pass |
| **Output** | Daily digest + email draft (only if judge passes) |

Full stage list: [docs/CHAT-LOOP.md](docs/CHAT-LOOP.md). Example run layout: [docs/DAILY-RUN.md](docs/DAILY-RUN.md).

### What counts as "jam"

Every promoted finding must have:

- A **source URL** (primary doc, repo, or guide)
- **How-to steps** (at least 3 concrete steps)
- **Evidence grade** A or B
- A clear benefit: `speed`, `robustness`, or `both`

See [config/jam-criteria.yaml](config/jam-criteria.yaml) and [templates/jam-item.example.json](templates/jam-item.example.json).

---

## Continue or resume later

Runs are resumable. The agent updates `runs/YYYY-MM-DD/RUN.md` after each stage.

**Pick up an in-progress day:**

```
Continue the dev scout loop for runs/YYYY-MM-DD/.
Read RUN.md and any feedback-*.md, then pick up where we left off.
```

**Re-research after thin results:**

```
The dev scout judge failed for runs/YYYY-MM-DD/.
Read gaps.md and feedback files, re-research the gaps, then update judge and outputs.
```

**Steer today's focus** (before or during a run):

```
For today's dev scout run, prioritize CI speed and test robustness.
Update runs/YYYY-MM-DD/GOAL.md accordingly, then continue the loop.
```

---

## Customize for your team

Fork the repo and tune these files — no code changes required.

| File | What to change |
|------|----------------|
| `templates/GOAL.md` | Daily mission and research questions |
| `config/lenses/*.yaml` | Themes to analyze (e.g. ship-faster, build-robust) |
| `config/judge.yaml` | Minimum findings, corroboration, quality bar |
| `config/sources.yaml` | Seed domains and discovery hints |
| `config/delivery.yaml` | Repo link shown in email briefs |

After editing, start a new chat with the same kickoff prompt. The agent reads your config on each run.

---

## Optional: email delivery

By default, findings are written to `runs/YYYY-MM-DD/06-email/email-draft.md` in the repo. To **also receive them by email**, set up Resend:

1. Copy [`.env.example`](.env.example) → `.env` (local) or add GitHub Actions secrets
2. Fill in:

| Variable | Purpose |
|----------|---------|
| `DEV_SCOUT_EMAIL` | Where the daily brief is sent |
| `RESEND_API_KEY` | Your Resend API key |
| `DELIVERY_FROM` | Verified sender address in Resend |

Without these, the loop still completes and writes drafts — send is skipped, not failed. Details: [docs/DELIVERY.md](docs/DELIVERY.md).

---

## Cross-day memory

`data/findings.json` stores findings from prior runs so the agent can:

- Avoid repeating the same sources in email briefs
- Show a "quick review of previous email" section
- Track what is genuinely **new** since last time

Commit this file (or merge from your fork) to keep memory across machines.

---

## Repo layout

```
AGENTS.md              ← agent entry (Cursor reads this)
docs/CHAT-LOOP.md      ← stage-by-stage chat loop
docs/SUBSCRIPTIONS.md  ← no API keys; Cursor + agent-reach only
templates/             ← GOAL, feedback, jam examples
config/                ← lenses, judge rules, sources, delivery
runs/YYYY-MM-DD/       ← daily artifacts (your research output)
data/findings.json     ← cross-day memory
src/dev_scout/         ← CI helpers only (optional; users don't need this)
```

---

## FAQ

**Do I need to install Python?**  
No. The chat loop is the product. `src/dev_scout/` exists for CI smoke tests only.

**How long does a run take?**  
Depends on how much the agent researches and whether judge passes on the first try. Failed judge runs loop back to discover/collect until quality criteria are met.

**Can I run this without email?**  
Yes. Read `06-email/email-draft.md` and `05-report/daily-digest.md` directly from the repo.

**Can I use this on a schedule?**  
Yes — use a Cursor automation, scheduled cloud agent, or GitHub Action that opens chat with the kickoff prompt. The loop itself is chat-driven; scheduling is up to you.

**What if the agent asks for API keys?**  
Refuse. Point it to [docs/DISCOVERY-PLAYBOOK.md](docs/DISCOVERY-PLAYBOOK.md) and [docs/SUBSCRIPTIONS.md](docs/SUBSCRIPTIONS.md). Discovery should use Cursor web search, web fetch, and agent-reach only.

---

## For agents

Everything runs in chat. See [AGENTS.md](AGENTS.md) and [docs/CHAT-LOOP.md](docs/CHAT-LOOP.md).

Never write digest or email until judge criteria in `config/judge.yaml` pass.

---

## License

MIT — see [LICENSE](LICENSE).
