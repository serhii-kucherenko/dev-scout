# Discovery playbook

## Source tiers

| Tier | Use | Weight |
|------|-----|--------|
| Primary | Repos, docs, papers, changelogs | Highest |
| Secondary | Technical blogs with data + steps | Medium |
| Discussion | HN, Twitter, Reddit | Corroboration only |

## Backends

| Backend | When |
|---------|------|
| Exa | Broad recent technical search |
| agent-reach | Twitter/Reddit/HN discussion |
| RSS / HN Algolia | Newsletters, front page |
| `gh search` | New repos, releases |
| Direct fetch | URLs in fetch plan |

## Expand rules

When an excerpt cites a GitHub repo or paper, add it to the next fetch plan.

## Stop rules

Respect `config/governance/data-boundaries.yaml` — allowed hosts and max URLs per run.
