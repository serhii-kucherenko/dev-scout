# Subscriptions only — no API keys

Dev Scout is designed to run entirely through **what you already pay for**. No OpenAI, Anthropic, Exa, or Resend keys.

Optional: set `DEV_SCOUT_EMAIL` (GitHub Actions variable/secret or local `.env`) so email drafts are addressed to you.

## What you use

| You already have | Dev Scout uses it for |
|------------------|----------------------|
| **Cursor Pro/Business** | Agent chat — the whole loop runs here |
| **Cursor web search** | Finding recent guides, repos, blog posts |
| **GitHub account** (`gh auth`) | Optional: `gh search` for repos and releases |
| **agent-reach** (in Cursor) | HN, Reddit, Twitter/X, GitHub, articles — free backends |

## What you do not need

- OpenAI API key
- Anthropic API key
- Google/Gemini API key
- Exa / Brave search API keys
- Resend or SMTP for the chat loop (email is a **draft** in the repo — `runs/…/06-email/email-draft.md` / `.eml`, addressed via `DEV_SCOUT_EMAIL`)

## If an agent asks for API keys

Refuse and use [DISCOVERY-PLAYBOOK.md](DISCOVERY-PLAYBOOK.md) instead: Cursor search + agent-reach + web fetch.

## Optional local setup

Only if you want CI to run Python smoke tests (not required for the chat loop):

```bash
pip install -e ".[dev]"
pytest
```

Only optional env for delivery address: `DEV_SCOUT_EMAIL` (see `.env.example` and [DELIVERY.md](DELIVERY.md)).
