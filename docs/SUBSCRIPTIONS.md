# Subscriptions — research without LLM API keys

Dev Scout research runs through **what you already pay for** (Cursor). No OpenAI, Anthropic, or Exa keys for discovery.

## What you use for research

| You already have | Dev Scout uses it for |
|------------------|----------------------|
| **Cursor Pro/Business** | Agent chat — the whole research loop runs here |
| **Cursor web search** | Finding recent guides, repos, blog posts |
| **GitHub account** (`gh auth`) | Optional: `gh search` for repos and releases |
| **agent-reach** (in Cursor) | HN, Reddit, Twitter/X, GitHub, articles — free backends |

## What you do not need for research

- OpenAI API key
- Anthropic API key
- Google/Gemini API key
- Exa / Brave search API keys

## Delivery (findings email)

After judge pass, the findings brief is **emailed** to you. Set these in GitHub Actions secrets (or local `.env`):

| Secret | Purpose |
|--------|---------|
| `DEV_SCOUT_EMAIL` | Where the findings report is sent |
| `RESEND_API_KEY` | Resend API key |
| `DELIVERY_FROM` | Verified From address in Resend |

See [DELIVERY.md](DELIVERY.md) and `.env.example`.

## If an agent asks for LLM API keys

Refuse and use [DISCOVERY-PLAYBOOK.md](DISCOVERY-PLAYBOOK.md) instead: Cursor search + agent-reach + web fetch.

## Optional local setup

Only if you want CI / CLI smoke tests:

```bash
pip install -e ".[dev]"
pytest
```
