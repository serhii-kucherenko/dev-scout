# Dev Scout Daily Digest — 2026-07-10

Mission: ship faster and build more robust software with AI-assisted dev.

Repo: https://github.com/serhii-kucherenko/dev-scout

---

## 1. Test agent behavior, not exact output strings (AgentAssay)

**Benefit:** robustness · **Setup:** days · **Grade:** A

**Why:** Many agent tests only check "did we get a response?" — so when the model drifts, tests still pass. AgentAssay makes small changes to prompts, tools, and context, then checks whether your tests catch them. It's cheaper than running hundreds of full retries on every change.

**Source:** https://arxiv.org/abs/2603.02601

**How-to:**

1. Define golden tasks for your agent workflow (inputs, expected behavioral properties, not exact strings).
2. Apply AgentAssay mutation operators on prompts, tool configs, model choice, and context windows.
3. Run SPRT-accelerated kill tests so you stop each mutant as soon as pass/fail is statistically clear.
4. Gate releases on mutation score and behavioral detection rate, not single-shot output equality.

**Evidence:** AgentAssay reports 78–100% cost reduction vs fixed-trial regression at equivalent statistical guarantees and 86% behavioral detection where binary testing detects 0%.

**Corroboration:** https://arxiv.org/pdf/2603.02601

**Try today:** Open one agent test. Replace a string-equality check with a behavior check (e.g. "must call the refund tool"). Break the prompt slightly and confirm the test fails.

---

## 2. Run agent shell commands in a disposable VM (Vercel Sandbox)

**Benefit:** robustness · **Setup:** hours · **Grade:** A

**Why:** When an agent runs shell commands on your laptop or CI host, a bad or hijacked command can read `.env`, keys, or reach your internal network. Sandbox runs each task in a throwaway Firecracker VM that disappears when done.

**Source:** https://vercel.com/docs/sandbox

**How-to:**

1. Install `@vercel/sandbox` and authenticate with `vercel link` + OIDC token (or access token for external CI).
2. Create a sandbox per agent task: `Sandbox.create({ runtime: 'node24', timeout: ms('5m') })`.
3. Seed workspace files, run commands via `sandbox.runCommand`, capture stdout/stderr only from the VM.
4. Snapshot after dependency install so subsequent runs skip setup; destroy sandbox when the task completes.

**Evidence:** Vercel Sandbox GA blog: sub-second starts, active-CPU billing, Blackbox dispatches parallel agents each in an isolated sandbox without resource contention.

**Corroboration:** https://vercel.com/blog/vercel-sandbox-is-now-generally-available

**Try today:** Install `@vercel/sandbox`, run one agent-generated script inside a sandbox, and note what never touched your host filesystem.

---

## 3. Run oxlint first to shrink CI lint time

**Benefit:** speed · **Setup:** minutes · **Grade:** A

**Why:** Full ESLint on a large monorepo can take minutes on every PR. oxlint catches most issues in seconds; ESLint only needs to handle what oxlint already cleared.

**Source:** https://oxc.rs/docs/guide/usage/linter.html

**How-to:**

1. Install oxlint as a dev dependency: `pnpm add -D oxlint` (or bun/npm equivalent).
2. Add `"lint:fast": "oxlint"` and change CI to run `oxlint` before `eslint`.
3. Migrate overlapping rules with `@oxlint/migrate` or use `eslint-plugin-oxlint` to disable duplicates in ESLint.
4. Wire oxlint into Turbo as a cached task so unchanged packages skip re-lint on cache hit.

**Evidence:** Oxlint benchmarks show 50–100× faster than ESLint on equivalent rule sets; a monorepo team reported oxlint as a 30–40% per-job speedup as a drop-in pre-check.

**Corroboration:** https://dev.to/jimmyyeung/journey-of-systematically-cut-our-monorepo-ci-time-in-half-ec8

**Try today:** `pnpm add -D oxlint`, add a `lint:fast` script, run it before ESLint in CI on one repo, and compare lint job time on the next PR.

---

## 4. Make the agent prove its tests actually catch bugs (incremental mutation testing)

**Benefit:** robustness · **Setup:** hours · **Grade:** A

**Why:** Agents write tests that run code but rarely assert meaningful outcomes — coverage looks high, regressions still slip through. Mutation testing makes tiny code changes and asks "did the test notice?" Incremental mode only checks changed files, so it finishes in minutes inside the agent sandbox instead of blocking shared CI for an hour.

**Source:** https://visdom-maturity-matrix.virtuslab.com/guides/development/mutation-testing-agent-validation

**How-to:**

1. Add Stryker (or PIT/mutmut for your stack) to the agent sandbox CI loop after unit tests pass.
2. Enable incremental mode (`--since` / diff-only) so only changed files are mutated.
3. Set a minimum mutation kill rate (start 70–80%) for agent-generated tests before the PR is submitted.
4. When mutants survive, feed the report back to the agent to strengthen assertions, then re-run in sandbox.

**Evidence:** VirtusLab L4 guide: incremental mutation on a ~200-line diff takes 3–5 minutes vs ~40 for full-suite runs; teams start at 70–80% kill threshold for agent tests.

**Corroboration:** https://tanhdev.com/series/ai-code-review-vibe-coding/part-4-review-pipeline-multi-agent/

**Try today:** Run Stryker with `--since` on tests the agent wrote for your last PR. Fix the first surviving mutant by adding a real assertion.

---

## 5. See which agent step burned time and tokens (OpenTelemetry gen_ai)

**Benefit:** robustness · **Setup:** hours · **Grade:** A

**Why:** "The agent was slow" or "the bill spiked" isn't enough to fix anything. One trace with a span per LLM call, tool call, and retrieval step shows exactly where the run failed, looped, or burned tokens — including across MCP servers and downstream services.

**Source:** https://developers.redhat.com/articles/2026/04/06/distributed-tracing-agentic-workflows-opentelemetry

**How-to:**

1. Install OpenTelemetry SDK and auto-instrument HTTP clients (HTTPx/FastAPI or your stack's equivalents).
2. Wrap each agent run in a root span; add child spans per LLM call, tool invocation, and retrieval step.
3. Set `gen_ai.request.model`, token usage attributes, and propagate W3C `traceparent` across MCP/tool calls.
4. Export via OTLP to a collector with tail-based sampling (keep 100% of errors/slow traces).

**Evidence:** Red Hat's agentic-workflow quickstart traces requests across app workloads, MCP servers, and Llama Stack; Geodocs spec defines gen_ai attribute set for vendor-neutral OTLP export.

**Corroboration:** https://geodocs.dev/ai-agents/agent-trace-instrumentation-spec

**Try today:** Wrap your agent's main run in one root span and add a child span around the first LLM call. Trigger one request and find that trace in your dashboard.

---

## 6. One AGENTS.md for everyone, small rules only where needed

**Benefit:** both · **Setup:** minutes · **Grade:** A

**Why:** Copying the same instructions into CLAUDE.md, AGENTS.md, and a huge always-on Cursor rule means they go stale at different speeds. Put shared basics in AGENTS.md; put folder-specific notes in small `.mdc` rules that load only for matching files.

**Source:** https://cursor.com/docs/context/rules

**How-to:**

1. Write cross-tool instructions in root `AGENTS.md` (mission, architecture, dependency policy).
2. Add focused `.cursor/rules/*.mdc` files with `globs` for path-specific behavior (e.g. `src/components/**/*.tsx`).
3. Keep each rule under 500 lines; reference canonical files with `@filename` instead of copying code.
4. Commit both to git; avoid parallel copies of the same policy in multiple adapter files.

**Evidence:** Cursor docs recommend AGENTS.md for simple portable instructions and .mdc rules for glob/intelligent activation; lean curated context beats dump-everything files on agent success and cost.

**Corroboration:** https://taskprio.com/cursor-rules

**Try today:** Move your repo's shared "how we work" text into `AGENTS.md`, delete duplicate copies, and add one `.mdc` rule scoped to `src/**/*.ts`.

---

## 7. Run parallel subagents while the prompt cache is still warm

**Benefit:** speed · **Setup:** hours · **Grade:** B

**Why:** Cached system prompts expire after about five minutes. Subagents that run one after another often miss the cache and pay full price for the same prefix again. Independent subagents started together right after a warm-up call share one cache window.

**Source:** https://dev.to/akaranjkar08/prompt-cache-orchestration-beat-the-5-min-ttl-miss-2026-2e31

**How-to:**

1. Mark stable system prompt, tool defs, and RAG context with `cache_control` so the prefix is cacheable.
2. Map your pipeline's independent subagent steps and measure inter-call gaps against the ~270s warm budget (5 min TTL minus safety margin).
3. Fire independent subagents in parallel at T=0 so they share one cache write instead of spanning multiple TTL windows.
4. Monitor `cache_read_input_tokens` and target 80%+ hit rate on the shared prefix after one tuning iteration.

**Evidence:** Cache-Warm Sequencing case: five 200s sequential subagents span three cache windows; parallel batch at T=0 finishes in ~200s with one write plus four reads — up to ~10× prefix cost reduction cited in the framework write-up.

**Corroboration:** https://platform.claude.com/docs/en/build-with-claude/prompt-caching

**Try today:** Find two subagent steps that don't need each other's output. Run them in parallel right after a cache-warm request and compare `cache_read_input_tokens` to your sequential run.

---

## 8. Give each parallel agent its own folder, share Turbo cache (git worktrees)

**Benefit:** speed · **Setup:** hours · **Grade:** B

**Why:** Two agents switching branches in one checkout overwrite each other's work and fight over local state. Git worktrees give each agent a separate folder for the same repo. Turbo remote cache lets both reuse build results for unchanged packages.

**Source:** https://turborepo.dev/docs/crafting-your-repository/constructing-ci

**How-to:**

1. Enable Turborepo remote caching (`turbo login`, `turbo link`, set `TURBO_TOKEN`/`TURBO_TEAM` in CI).
2. For each agent task, `git worktree add ../agent-N feat/agent-N` instead of switching branches in-place.
3. Run `turbo run lint typecheck test build --filter=...[origin/main]` inside each worktree.
4. Remove worktrees when done: `git worktree remove ../agent-N`.

**Evidence:** Turborepo 3.0 documents worktree-safe shared cache; a 4-app monorepo case study reports cold CI ~120s vs warm ~12s with parallel agent worktrees.

**Corroboration:** https://callsphere.ai/blog/vw8h-build-ai-agent-cicd-turborepo-monorepo-2026.md

**Try today:** `git worktree add ../agent-b feat/other-branch`, run `turbo build` in both folders without changing code, and confirm the second run reports a remote cache hit.
