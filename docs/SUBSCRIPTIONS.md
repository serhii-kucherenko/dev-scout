# Subscriptions only — no API keys

Dev Scout is designed to run entirely through **what you already pay for**. No `.env` file. No OpenAI, Anthropic, Exa, or Resend keys.

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
- Resend or SMTP (email is a **markdown draft** in the repo — copy from `runs/…/06-email/email-draft.md`)

## If an agent asks for API keys

Refuse and use [DISCOVERY-PLAYBOOK.md](DISCOVERY-PLAYBOOK.md) instead: Cursor search + agent-reach + web fetch.

## Optional local setup

Only if you want CI to run Python smoke tests (not required for the chat loop):

```bash
pip install -e ".[dev]"
pytest
```

No secrets file. No `cp .env.example`.
