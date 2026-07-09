# Dev Scout Weekly Digest — 2026-W28

This week's run was rebuilt from primary docs and real corroboration after discarding an earlier placeholder-heavy draft.

## Top jam

### OpenAI Evals meta-evals plus PR gating

**Why:** The highest leverage eval workflow is not "run a dataset once"; it is adding meta-evals and a pull-request gate so rubric regressions are caught before merge.

**Benefit:** robustness | **Grade:** A

**Evidence:** The build guide explicitly recommends meta-evals and says good model-graded evals should report `metascore/` accuracy close to `1.0`; the repo workflow automatically runs new eval YAMLs on pull requests.

**Source:** https://github.com/openai/evals/blob/main/docs/build-eval.md

**How-to:** https://github.com/openai/evals/blob/main/docs/build-eval.md

**Steps:**
  1. Put your dataset in `evals/registry/data/<eval_name>/samples.jsonl` and register it in `evals/registry/evals/<eval_name>.yaml`.
  2. Run `oaieval <model> <eval_name>` locally to validate the task and rubric.
  3. Add labeled choice data and a meta-eval until `metascore/` is close to `1.0`.
  4. Copy the repo's PR workflow pattern so new eval YAMLs get a lightweight CI check automatically.

**Corroboration:** https://github.com/openai/evals/blob/main/.github/workflows/test_eval.yaml

**Try Monday:** Turn one fragile prompt workflow into a 20-25 sample eval before the next prompt or model tweak.

### AI Gateway provider sorting by cost, TTFT, or TPS

**Why:** When a model is available from several providers, the gateway can route for low cost, low first-token latency, or high throughput without app-side provider switching code.

**Benefit:** speed | **Grade:** A

**Evidence:** The docs expose sort controls for `cost`, `ttft`, and `tps`, while the changelog explains that ranking updates at request time as provider prices and latency shift.

**Source:** https://vercel.com/docs/ai-gateway/models-and-providers/provider-filtering-and-ordering

**How-to:** https://vercel.com/docs/ai-gateway/models-and-providers/provider-filtering-and-ordering

**Steps:**
  1. Route the request through AI Gateway instead of calling one provider directly.
  2. Set `providerOptions.gateway.sort` to `cost`, `ttft`, or `tps`.
  3. Combine it with `only` or `order` if you have vendor constraints.
  4. Read the returned routing metadata so you can inspect the actual execution order and metrics.

**Corroboration:** https://vercel.com/changelog/sort-providers-by-cost-latency-or-throughput-on-ai-gateway

**Try Monday:** Switch one interactive coding endpoint to `ttft` sorting and compare response feel.

### AI Gateway model fallbacks without app-side retry code

**Why:** Cross-provider and cross-model fallback lets you survive outages or incompatibilities without custom retry orchestration in the application layer.

**Benefit:** robustness | **Grade:** A

**Evidence:** The fallback docs show ordered retries across primary and backup models and providers; Vercel's architecture write-up describes automatic rerouting and retries when provider health degrades.

**Source:** https://vercel.com/docs/ai-gateway/models-and-providers/model-fallbacks

**How-to:** https://vercel.com/docs/ai-gateway/models-and-providers/model-fallbacks

**Steps:**
  1. Keep your preferred model in `model`.
  2. Add a `providerOptions.gateway.models` array for your backups.
  3. Add `order` if provider preference matters for each model.
  4. Log `modelAttempts` and `providerAttempts` so failures are visible instead of silent.

**Corroboration:** https://vercel.com/blog/how-ai-gateway-runs-on-fluid-compute

**Try Monday:** Add one backup model to a non-critical route and capture fallback metadata in logs.

### Scheduled Claude Code workflows with repo-scoped subagents

**Why:** Claude Code's GitHub Action can run on comments or cron while still obeying `CLAUDE.md` and custom agents that live in the repo.

**Benefit:** both | **Grade:** A

**Evidence:** Official docs provide quick setup, manual install, cron examples, and v1 workflow syntax; the GitHub discussion shows the `--agent` pattern for scheduled custom subagents.

**Source:** https://docs.anthropic.com/en/docs/claude-code/github-actions

**How-to:** https://docs.anthropic.com/en/docs/claude-code/github-actions

**Steps:**
  1. Run `/install-github-app` or manually install the Claude GitHub App.
  2. Add `ANTHROPIC_API_KEY` and a workflow under `.github/workflows/`.
  3. Put project rules in `CLAUDE.md`.
  4. Store specialized jobs in `.claude/agents/` and invoke them via `claude_args: --agent <name>`.

**Corroboration:** https://github.com/anthropics/claude-code-action/discussions/576

**Try Monday:** Schedule one daily repo-maintenance workflow with a dedicated subagent.

### Roots-aware MCP filesystem server pattern

**Why:** The official MCP filesystem server is now a practical template for safe agent file access: explicit allowed directories, Roots-based live updates, and copyable configs for popular clients.

**Benefit:** both | **Grade:** A

**Evidence:** Primary docs include concrete `npx`, Docker, VS Code, and Claude Desktop configs plus Roots-based runtime directory updates; the repo is the official MCP reference server collection.

**Source:** https://github.com/modelcontextprotocol/servers

**How-to:** https://github.com/modelcontextprotocol/servers/blob/main/src/filesystem/README.md

**Steps:**
  1. Choose the filesystem server when you want scoped file access instead of broad shell power.
  2. Register it in Claude Desktop or VS Code and pass only the directories the agent should touch.
  3. Prefer Roots-capable clients so allowed paths can change without a server restart.
  4. If the server fails under NVM, switch to an absolute `node` or `npx` path or a wrapper script.

**Corroboration:** https://github.com/modelcontextprotocol/servers/issues/64 and https://news.ycombinator.com/item?id=47380270

**Try Monday:** Add a filesystem MCP server to one sandbox repo and keep it pinned to a single folder at first.

### Codex CLI review-before-push workflow

**Why:** Codex now combines local agent mode, a separate review agent, subagents, MCP, and cloud tasks in one CLI, which lowers the friction to adopt a review-before-push loop.

**Benefit:** both | **Grade:** A

**Evidence:** OpenAI describes the CLI as open source and built in Rust for speed and efficiency, and documents separate review, subagents, MCP, and cloud-task flows in the same tool.

**Source:** https://developers.openai.com/codex/cli

**How-to:** https://developers.openai.com/codex/quickstart

**Steps:**
  1. Install Codex and run it inside the project you want it to edit.
  2. Keep Git checkpoints before and after tasks.
  3. Use the built-in review pass before commit or push.
  4. Add subagents, MCP servers, or cloud tasks only after the base local workflow feels predictable.

**Corroboration:** https://developers.openai.com/codex/quickstart

**Try Monday:** Require a second Codex review pass for every Codex-generated diff on one repo.

## Lens coverage

### tooling-setups
- [Roots-aware MCP filesystem server pattern](https://github.com/modelcontextprotocol/servers)
- [Scheduled Claude Code workflows with repo-scoped subagents](https://docs.anthropic.com/en/docs/claude-code/github-actions)
- [Codex CLI review-before-push workflow](https://developers.openai.com/codex/cli)

### build-robust
- [OpenAI Evals meta-evals plus PR gating](https://github.com/openai/evals/blob/main/docs/build-eval.md)

### model-workflows
- [AI Gateway provider sorting by cost, TTFT, or TPS](https://vercel.com/docs/ai-gateway/models-and-providers/provider-filtering-and-ordering)

### production-patterns
- [AI Gateway model fallbacks without app-side retry code](https://vercel.com/docs/ai-gateway/models-and-providers/model-fallbacks)

## Skipped

- No `ship-faster` item was promoted this week because the strongest recent sources explained workflows but did not publish benchmark-quality speed evidence.
