# Dev Scout Daily Digest — 2026-07-09

Actionable jam for faster, more robust development.

Repo: https://github.com/serhii-kucherenko/dev-scout

## Top jam

### Cache stable prompt prefixes to cut LLM cost and latency

**Why:** Marking the unchanging part of a prompt (system instructions, tool defs, RAG/codebase context) as cacheable makes repeat calls reuse it at ~10% of input price and skip prefix compute, so cost and time-to-first-token drop sharply.

**Benefit:** both | **Grade:** A

**Evidence:** Anthropic reports up to 90% lower input cost (cache reads at 0.1x) and up to 85% lower time-to-first-token; documented cases cut a bill from $720 -> $72/mo and per-page generation from $0.42 -> $0.06 (86%).

**Source:** https://platform.claude.com/docs/en/build-with-claude/prompt-caching

**How-to:** https://platform.claude.com/docs/en/build-with-claude/prompt-caching

**Steps:**
  1. Identify the stable prefix (system prompt, tool defs, long context) that repeats across calls and ensure it meets the model minimum (~1,024 tokens).
  2. Add `cache_control: {type: 'ephemeral'}` to those blocks; keep the prefix byte-identical (no injected timestamps, no reordered tools).
  3. Log `cache_read_input_tokens` and `cache_creation_input_tokens` from the response usage to verify hit rates.
  4. For batch/agentic runs, fire calls within the TTL (5-min default or the 1-hour option) and pre-warm the cache before user traffic.

**Try today:** Add cache_control to the system prompt of one high-volume call and check cache_read_input_tokens on the second request.


### Swap pip for uv to cut install and CI time

**Why:** uv is a Rust drop-in for pip/venv that resolves and installs dependencies in a fraction of the time, so local setup and every cold-cache CI run get dramatically faster.

**Benefit:** speed | **Grade:** A

**Evidence:** Real Python measured ~8x faster than pip (21.4s -> 2.6s installing JupyterLab); a widely cited uncached install dropped 38s -> 3s; one team cut a five-project CI suite from ~9 min to ~4.5 min.

**Source:** https://docs.astral.sh/uv/

**How-to:** https://docs.astral.sh/uv/getting-started/

**Steps:**
  1. Install uv (`curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`), then confirm with `uv --version`.
  2. In the project, run `uv init` if there is no pyproject.toml, then `uv add -r requirements.txt` to import existing deps and generate uv.lock.
  3. Commit pyproject.toml and uv.lock; recreate environments with `uv sync` and run commands via `uv run <cmd>` instead of activating a venv.
  4. Swap the CI install step to `uv sync --frozen` for deterministic, cache-fast installs, and compare the install stage time before/after.

**Try today:** Run `uv sync` on one repo and switch its CI install step to uv, then compare the install stage timing.


### Add a merge-queue integrity check so bad merges can't land silently

**Why:** The April 2026 GitHub merge-queue bug silently reverted already-merged work while CI stayed green, because branch protection validates the temp commit, not what actually lands on main. A tree-hash / merge-base check makes that divergence impossible to miss.

**Benefit:** robustness | **Grade:** A

**Evidence:** The April 23, 2026 GitHub merge-queue bug silently corrupted 658 repositories and 2,092 PRs for ~4.5 hours with green CI and no status-page entry; recovery had to be done by hand.

**Source:** https://mergify.com/blog/merge-queue-is-critical-infrastructure

**How-to:** https://trunk.io/blog/what-happens-if-a-merge-queue-builds-on-the-wrong-commit

**Steps:**
  1. Add a post-merge CI job that recomputes the expected tree for each landed commit and compares it to the tested PR commit's tree (modulo merge-mode normalization); fail loudly on mismatch.
  2. Verify the merge group's base equals the current head of the target branch before the merge finalizes, and block if they diverge.
  3. Until you trust the queue, cap merge-group size to 1 (sequential) for squash groups to avoid the multi-PR failure combination.
  4. Keep enough audit trail (tested commit SHAs) that you can reconstruct what CI actually signed off on after the fact.

**Try today:** Add a post-merge job that compares the landed tree hash to the tested PR's tree and alerts on mismatch.


### Run mutation testing to find tests that don't actually assert

**Why:** High line coverage can hide tests that execute code without verifying behavior. Mutation testing injects small bugs and checks your suite catches them, exposing real gaps a coverage number will not.

**Benefit:** robustness | **Grade:** A

**Evidence:** Teams with 95-98% line coverage found ~23% of mutants survived and uncovered 12 real undetected bugs; another 98%-coverage suite still let a data-corrupting bug reach production because tests never asserted the outcome.

**Source:** https://stryker-mutator.io/docs/

**How-to:** https://stryker-mutator.io/docs/

**Steps:**
  1. Pick the mutation runner for your stack (Stryker for JS/TS/.NET, PIT for Java, mutmut for Python, cargo-mutants for Rust).
  2. Scope the first run to one core module so it finishes fast, since mutation testing is CPU-heavy.
  3. Review surviving mutants and, for each, add or strengthen an assertion until it is killed instead of chasing the score.
  4. Wire it into CI nightly (or on changed files only) against critical domain logic, not every PR.

**Try today:** Run the mutation runner on one core module and fix the first three surviving mutants with real assertions.


### Turn on Turborepo remote caching in CI

**Why:** Remote caching shares task outputs across teammates and CI runners, so unchanged builds/tests/lints download instead of re-running, collapsing duplicated work on every PR.

**Benefit:** speed | **Grade:** A

**Evidence:** Makeswift cut CI pipeline time 65% (commit-to-deploy ~20 min -> under 1 min); the Next.js team cut publish times 80%; a 6-month monorepo retrospective reported full builds down ~50% (22 -> 11 min p50) at a 94% cache hit rate.

**Source:** https://turborepo.dev/docs/core-concepts/remote-caching

**How-to:** https://turborepo.dev/docs/core-concepts/remote-caching

**Steps:**
  1. Define cacheable tasks in turbo.json with precise `inputs` and `outputs` so content hashes are correct.
  2. Connect a remote cache: managed via `npx turbo login` + `npx turbo link`, or a self-hosted cache endpoint with a token.
  3. Run a build twice locally and confirm the second run reports a remote cache hit.
  4. In CI, pass the cache token/team env vars and run `turbo run build test lint`; verify the logs show 'remote cache hit'.

**Try today:** Enable remote caching on one repo and re-run a green build to confirm a remote cache hit.


## All findings by lens

### build-robust
- [Add a merge-queue integrity check so bad merges can't land silently](https://mergify.com/blog/merge-queue-is-critical-infrastructure)
- [Run mutation testing to find tests that don't actually assert](https://stryker-mutator.io/docs/)

### model-workflows
- [Cache stable prompt prefixes to cut LLM cost and latency](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

### production-patterns
- [Give every PR an ephemeral full-stack preview environment](https://getautonoma.com/blog/per-pr-preview-environments-when-ci-green-isnt-enough)

### ship-faster
- [Turn on Turborepo remote caching in CI](https://turborepo.dev/docs/core-concepts/remote-caching)

### tooling-setups
- [Swap pip for uv to cut install and CI time](https://docs.astral.sh/uv/)
