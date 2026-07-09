To: kucherenko.web@gmail.com
Subject: Dev Scout 2026-W28 - 5 source-backed ways to ship faster and safer

Hi Serhii,

I rebuilt this week's Dev Scout run from primary docs and real corroboration after discarding a thinner placeholder draft. Top takeaways:

1. OpenAI Evals meta-evals plus PR gating (robustness)
   Source: https://github.com/openai/evals/blob/main/docs/build-eval.md
   Why it matters: This is the cleanest path from "we should add evals someday" to "model or prompt regressions stop merging silently."
   Steps:
     1. Put your dataset in `evals/registry/data/<eval_name>/samples.jsonl`.
     2. Register it in `evals/registry/evals/<eval_name>.yaml`.
     3. Add a meta-eval until `metascore/` is close to `1.0`.
     4. Gate new eval YAMLs in CI with a lightweight `oaieval` run.
   Try Monday: Turn one fragile prompt workflow into a 20-25 sample eval before the next prompt or model tweak.

2. AI Gateway provider sorting by cost, TTFT, or TPS (speed)
   Source: https://vercel.com/docs/ai-gateway/models-and-providers/provider-filtering-and-ordering
   Why it matters: You can optimize for cost or latency without rewriting app code every time provider performance shifts.
   Steps:
     1. Route one endpoint through AI Gateway.
     2. Set `providerOptions.gateway.sort` to `cost`, `ttft`, or `tps`.
     3. Add `only` or `order` if you have vendor constraints.
     4. Inspect routing metadata to see what actually ran.
   Try Monday: Switch one interactive coding endpoint to `ttft` sorting and compare perceived responsiveness.

3. AI Gateway model fallbacks without app-side retry code (robustness)
   Source: https://vercel.com/docs/ai-gateway/models-and-providers/model-fallbacks
   Why it matters: Backup models and providers can be declared once in the gateway instead of hand-coded in every app path.
   Steps:
     1. Keep your preferred model in `model`.
     2. Add backup entries in `providerOptions.gateway.models`.
     3. Add `order` if provider preference matters.
     4. Log `modelAttempts` and `providerAttempts`.
   Try Monday: Add one backup model to a non-critical route and capture fallback metadata in logs.

4. Scheduled Claude Code workflows with repo-scoped subagents (both)
   Source: https://docs.anthropic.com/en/docs/claude-code/github-actions
   Why it matters: Repo-native automation is now straightforward enough to use for daily maintenance jobs instead of a one-off bot project.
   Steps:
     1. Run `/install-github-app` or manually install the Claude GitHub App.
     2. Add `ANTHROPIC_API_KEY` and a workflow file.
     3. Put project rules in `CLAUDE.md`.
     4. Invoke a custom repo agent via `claude_args: --agent <name>`.
   Try Monday: Schedule one daily maintenance workflow with a dedicated subagent.

5. Roots-aware MCP filesystem server pattern (both)
   Source: https://github.com/modelcontextprotocol/servers
   Why it matters: This is one of the clearest "safe agent access" patterns I found this week: explicit directories, live roots updates, and easy client configs.
   Steps:
     1. Choose the filesystem server for scoped file access.
     2. Register it in Claude Desktop or VS Code with only the directories you want exposed.
     3. Prefer Roots-capable clients for live path updates.
     4. If NVM breaks startup, switch to absolute `node` or `npx` paths.
   Try Monday: Add a filesystem MCP server to one sandbox repo and keep it pinned to a single folder first.

Bonus:
- Codex CLI now has a credible review-before-push loop built in: https://developers.openai.com/codex/cli

Full digest:
- runs/2026-W28/05-report/weekly-digest.md

Email draft path:
- runs/2026-W28/06-email/email-draft.md
