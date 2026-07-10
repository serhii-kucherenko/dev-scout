To: $DEV_SCOUT_EMAIL
Subject: Dev Scout 2026-07-10 — 8 new ways to ship faster / build safer

Dev Scout — 2026-07-10

Mission: ship faster & build more robust software with AI-assisted dev.

Repo: https://github.com/serhii-kucherenko/dev-scout

Quick review of previous email (2026-07-09):
- Cache stable prompt prefixes to cut LLM cost and latency (both) — https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Swap pip for uv to cut install and CI time (speed) — https://docs.astral.sh/uv/
- Add a merge-queue integrity check so bad merges can't land silently (robustness) — https://mergify.com/blog/merge-queue-is-critical-infrastructure
- Run mutation testing to find tests that don't actually assert (robustness) — https://stryker-mutator.io/docs/
- Turn on Turborepo remote caching in CI (speed) — https://turborepo.dev/docs/core-concepts/remote-caching

Skip those unless you still need to act on one.

New since last brief: 8 (speed=3, robustness=4, both=1).
Each tag is benefit · setup time · evidence grade — skip what doesn't fit your stack.

1. Test agent behavior, not exact output strings  [robustness · ~days · grade A]
   Why it matters: Agent tests often pass even when behavior is wrong, because they only check "did we get a response?" AgentAssay nudges prompts and tools and asks whether your tests notice — without running hundreds of expensive full retries.
   Do this next: Pick one agent test. Stop comparing the full output string. Check a behavior instead (e.g. "must call the refund tool" or "must not mention internal IDs"). Break the prompt slightly and confirm the test fails.
   Link: https://arxiv.org/abs/2603.02601

2. Run agent shell commands in a disposable VM, not on your laptop  [robustness · ~hours · grade A]
   Why it matters: When an agent runs `npm test` or arbitrary shell on your machine, a mistake or injection can read `.env`, keys, or your internal network. Vercel Sandbox gives each run its own short-lived VM that goes away when finished.
   Do this next: Install `@vercel/sandbox`, run one agent-generated script inside a sandbox, and note what never touched your host filesystem.
   Link: https://vercel.com/docs/sandbox

3. Run oxlint first to shrink CI lint time  [speed · ~minutes · grade A]
   Why it matters: Full ESLint on a large monorepo can take minutes every PR. oxlint catches most problems in seconds; ESLint only needs to run on what oxlint already cleared.
   Do this next: `pnpm add -D oxlint`, add a `lint:fast` script, run it before ESLint in CI on one repo, and compare lint job time on the next PR.
   Link: https://oxc.rs/docs/guide/usage/linter.html

4. Make the agent prove its tests actually catch bugs  [robustness · ~hours · grade A]
   Why it matters: Agents write tests that execute code but don't assert much — coverage looks great, regressions slip through. Mutation testing makes tiny code changes and checks if tests fail. Incremental mode only touches changed files, so it finishes in a few minutes in the agent sandbox.
   Do this next: Run Stryker with `--since` on tests the agent wrote for your last PR. Open the report and fix the first surviving mutant by adding a real assertion.
   Link: https://visdom-maturity-matrix.virtuslab.com/guides/development/mutation-testing-agent-validation

5. See which agent step burned time and tokens  [robustness · ~hours · grade A]
   Why it matters: "The agent was slow" or "the bill spiked" isn't actionable. One trace with a span per LLM call, tool, and retrieval step shows exactly where the run went wrong or looped.
   Do this next: Wrap your agent's main run in one root OpenTelemetry span and add a child span around the first LLM call. Trigger one request and find that trace in your dashboard (Tempo, Datadog, Honeycomb, etc.).
   Link: https://developers.redhat.com/articles/2026/04/06/distributed-tracing-agentic-workflows-opentelemetry

6. One AGENTS.md for everyone, small rules only where needed  [both · ~minutes · grade A]
   Why it matters: Pasting the same instructions into CLAUDE.md, AGENTS.md, and a huge always-on Cursor rule means they drift apart. Shared basics live in AGENTS.md; folder-specific notes live in small `.mdc` rules that load only for matching files.
   Do this next: Move your repo's shared "how we work" text into `AGENTS.md`. Delete duplicate copies. Add one `.cursor/rules/typescript.mdc` scoped to `src/**/*.ts` with only TS-specific guidance.
   Link: https://cursor.com/docs/context/rules

7. Run parallel subagents while the prompt cache is still warm  [speed · ~hours · grade B]
   Why it matters: Cached system prompts expire after about five minutes. Subagents that run one-by-one often miss the cache and pay full price for the same prefix repeatedly. Independent subagents started together right after a warm-up call share one cache window.
   Do this next: Find two subagent steps that don't need each other's output. Run them in parallel right after a cache-warm request. Compare `cache_read_input_tokens` to your usual sequential run.
   Link: https://dev.to/akaranjkar08/prompt-cache-orchestration-beat-the-5-min-ttl-miss-2026-2e31

8. Give each parallel agent its own folder, share Turbo cache  [speed · ~hours · grade B]
   Why it matters: Two agents switching branches in one checkout overwrite each other's work and fight over local state. Git worktrees = separate folders, same repo. Turbo remote cache means both still reuse build results for unchanged packages.
   Do this next: `git worktree add ../agent-b feat/other-branch`. Run `turbo build` in both folders without changing code. Confirm the second run reports a remote cache hit.
   Link: https://turborepo.dev/docs/crafting-your-repository/constructing-ci

Full steps and evidence: runs/2026-07-10/05-report/daily-digest.md
