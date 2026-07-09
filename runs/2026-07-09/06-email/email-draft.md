To: kucherenko.web@gmail.com // pragma: allowlist secret
Subject: Dev Scout 2026-07-09 — 5 new ways to ship faster / build safer

Dev Scout — 2026-07-09

Mission: ship faster & build more robust software with AI-assisted dev.

Repo: https://github.com/serhii-kucherenko/dev-scout

Quick review of previous email (2099-W01):
- MCP servers for IDE workflows (both)
- Claude Code CLI setup (both)
- Eval harness for LLM regressions (robustness)
- Ralph loop agent harness (speed)
- LangGraph production deploy patterns (robustness)

Do not re-read those unless you still need to act on them.

New since last brief: 5 (speed=3, robustness=3).
Tags read benefit · setup effort · evidence grade — skip anything that doesn't fit.

1. Cache stable prompt prefixes to cut LLM cost and latency  [both · ~minutes to set up · grade A]
   Why it matters: Marking the unchanging part of a prompt (system instructions, tool defs, RAG/codebase context) as cacheable makes repeat calls reuse it at ~10% of input price and skip prefix compute, so cost and time-to-first-token drop sharply.
   Try: Add cache_control to the system prompt of one high-volume call and check cache_read_input_tokens on the second request.
   Link: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

2. Swap pip for uv to cut install and CI time  [speed · ~minutes to set up · grade A]
   Why it matters: uv is a Rust drop-in for pip/venv that resolves and installs dependencies in a fraction of the time, so local setup and every cold-cache CI run get dramatically faster.
   Try: Run `uv sync` on one repo and switch its CI install step to uv, then compare the install stage timing.
   Link: https://docs.astral.sh/uv/

3. Add a merge-queue integrity check so bad merges can't land silently  [robustness · ~hours to set up · grade A]
   Why it matters: The April 2026 GitHub merge-queue bug silently reverted already-merged work while CI stayed green, because branch protection validates the temp commit, not what actually lands on main. A tree-hash / merge-base check makes that divergence impossible to miss.
   Try: Add a post-merge job that compares the landed tree hash to the tested PR's tree and alerts on mismatch.
   Link: https://mergify.com/blog/merge-queue-is-critical-infrastructure

4. Run mutation testing to find tests that don't actually assert  [robustness · ~hours to set up · grade A]
   Why it matters: High line coverage can hide tests that execute code without verifying behavior. Mutation testing injects small bugs and checks your suite catches them, exposing real gaps a coverage number will not.
   Try: Run the mutation runner on one core module and fix the first three surviving mutants with real assertions.
   Link: https://stryker-mutator.io/docs/

5. Turn on Turborepo remote caching in CI  [speed · ~hours to set up · grade A]
   Why it matters: Remote caching shares task outputs across teammates and CI runners, so unchanged builds/tests/lints download instead of re-running, collapsing duplicated work on every PR.
   Try: Enable remote caching on one repo and re-run a green build to confirm a remote cache hit.
   Link: https://turborepo.dev/docs/core-concepts/remote-caching

Full detail (all steps + evidence): runs/2026-07-09/05-report/daily-digest.md
