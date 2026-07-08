# Discovery playbook

**No external API keys.** Use the user's existing Cursor subscription plus free tools below. Never ask for OpenAI, Anthropic, Exa, or other paid API keys.

## What powers the loop

| Tool | Role | Cost |
|------|------|------|
| **Cursor Agent (this chat)** | Research, lens analysis, judge, writing digest/email | Cursor subscription |
| **Cursor web search** | Discover recent posts, docs, guides | Included in Cursor |
| **agent-reach** | Twitter, Reddit, HN, GitHub, articles, RSS | Free backends (see skill) |
| **`gh search`** | GitHub repos/issues (if `gh auth` already set up) | Free with GitHub account |
| **Web fetch** | Read primary sources (docs, READMEs, blogs) | Free |
| **HN Algolia** | HN front-page / search JSON API | Free, no key |

## Source tiers

| Tier | Use | Weight |
|------|-----|--------|
| Primary | Repos, docs, papers, changelogs | Highest |
| Secondary | Technical blogs with data + steps | Medium |
| Discussion | HN, Twitter, Reddit | Corroboration only |

## Search order (agent)

1. Cursor web search for lens-specific queries from `config/sources.yaml`
2. agent-reach for discussion + GitHub + articles (read `agent-reach` skill)
3. `gh search repos` / `gh search issues` when GitHub is the target
4. Direct fetch of URLs found above
5. HN Algolia for recent AI/dev threads

## Expand rules

When an excerpt cites a GitHub repo or paper, add it to the next fetch plan.

## Stop rules

Respect `config/governance/data-boundaries.yaml` — allowed hosts and max URLs per run.

## Do not use

- OpenAI / Anthropic / Gemini API keys for this harness
- Exa / Brave paid search APIs
- Any setup step that asks the user to paste API keys

The user runs everything through **Cursor chat subscriptions they already pay for**.
