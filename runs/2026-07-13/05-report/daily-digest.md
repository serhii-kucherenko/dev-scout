# Dev Scout Daily Digest — 2026-07-13

Actionable jam for faster, more robust development with AI-assisted software work.

Repo: https://github.com/serhii-kucherenko/dev-scout

## Building AI systems

Practices for designing, evaluating, and operating AI agents and LLM features.

### Defer tool loading so agents search for tools instead of hauling them into every prompt

**Why:** Large MCP and tool catalogs crush context windows and hurt tool selection; on-demand discovery preserves prompt cacheability and improves accuracy.

**Benefit:** both | **Setup:** hours | **Grade:** A

**Evidence:** Anthropic says Tool Search cut context usage from roughly 77K tokens to about 8.7K, preserved 95% of the context window, reduced token usage 85%, and improved MCP-eval accuracy from 49% to 74% on Opus 4 and from 79.5% to 88.1% on Opus 4.5.

**Source:** https://www.anthropic.com/engineering/advanced-tool-use

**How-to:** https://www.anthropic.com/engineering/advanced-tool-use

**Steps:**
  1. Keep only a small always-loaded core toolset and add a Tool Search tool to the initial prompt so the agent starts with discovery rather than a giant schema dump.
  2. Mark the long tail of tools or even whole MCP servers with defer_loading so they are discovered on demand instead of occupying context from turn one.
  3. Keep the shared system prompt and core tools byte-stable across calls so prompt caching still hits while deferred tools are pulled in only after search.
  4. Measure token use and tool-selection accuracy before and after the change, then promote only the tools that are truly used on nearly every task back into the always-loaded set.

**Try today:** Take one 20-plus-tool setup, defer-load the rarely used tools, and compare prompt size plus tool-choice accuracy on the next five real tasks.

### Audit coding benchmarks with investigator agents before you trust the score

**Why:** Broken tasks and contaminated benchmarks can hide real regressions or fake progress, so benchmark quality needs its own QA loop.

**Benefit:** robustness | **Setup:** hours | **Grade:** A

**Evidence:** OpenAI says its SWE-Bench Pro audit pipeline flagged 200 tasks (27.4%) as broken, human reviewers labeled 249 (34.1%) broken, and the company now estimates that roughly 30% of the dataset is broken.

**Source:** https://openai.com/index/separating-signal-from-noise-coding-evaluations/

**How-to:** https://openai.com/index/separating-signal-from-noise-coding-evaluations/

**Steps:**
  1. Run an automated filter over prompts, hidden tests, model attempts, and failure traces so you flag suspect benchmark tasks before treating misses as capability gaps.
  2. Give investigator agents access to the task repository and environment so they can run tests, inspect files, and classify likely failure modes instead of guessing from the score alone.
  3. Add multi-review human adjudication for flagged tasks, and escalate disagreements or low-confidence labels until you know whether the problem is real or a dataset flaw.
  4. Publish benchmark caveats, quarantine broken tasks, and stop headline reporting when the dataset no longer reflects actual engineering capability.

**Try today:** Take the benchmark or internal eval you cite most often, audit the first 20 recent failures with an investigator-agent plus human review, and see how many are actually dataset defects.

## Using AI to build software

Practices for teams using coding agents to ship and maintain regular application software.

### Split long agent projects into recursive planners and isolated workers

**Why:** Hierarchical ownership avoids shared-lock bottlenecks and keeps many agents moving on one codebase without waiting on each other.

**Benefit:** speed | **Setup:** hours | **Grade:** A

**Evidence:** Cursor says hundreds of concurrent agents wrote over 1 million lines across 1,000 files in a week, and its deeper harness write-up says the system later peaked at roughly 1,000 commits per hour across 10 million tool calls with root planners, subplanners, and isolated workers.

**Source:** https://cursor.com/blog/scaling-agents

**How-to:** https://cursor.com/blog/self-driving-codebases

**Steps:**
  1. Create one root planner prompt whose only job is to own the user goal and emit specific task handoffs; keep it out of direct coding work.
  2. Let the root planner spawn subplanners whenever a slice of the problem can be owned independently, so planning fans out recursively instead of becoming one giant static plan.
  3. Give each worker its own copy of the repo or worktree and require a single written handoff back to the requesting planner instead of direct worker-to-worker coordination.
  4. Delete shared locking files and central integrators unless runtime data proves you need them; keep a separate reconciliation pass for final cleanup instead of blocking every worker on perfect intermediate state.

**Try today:** Run one thorny multi-file task with one planner prompt and three isolated worker branches/worktrees, then compare waiting time against your usual single-agent loop.

### Put a contextual reviewer in front of risky agent actions

**Why:** A small classifier agent cuts unsafe tool calls without turning autonomy into constant approval fatigue.

**Benefit:** robustness | **Setup:** hours | **Grade:** A

**Evidence:** Cursor reports training against 6,122 labeled rows; the Auto-review classifier blocks only about 4% of reviewed actions, and only about 7% of total Auto-review chats lead to an interruption versus roughly 40% blocked actions some enterprises had seen before.

**Source:** https://cursor.com/blog/agent-autonomy-auto-review

**How-to:** https://cursor.com/blog/agent-autonomy-auto-review

**Steps:**
  1. Collect representative internal agent traces, deduplicate them into labeled eval rows, and mark which actions should pass versus block in normal development work.
  2. Add synthetic cases for the failures you rarely see in organic usage, especially secret reads, production data writes, untrusted instructions, and commands with large side effects.
  3. Run the reviewer in the same execution path as the parent agent so it can inspect files or nearby context before deciding, rather than forcing an extra approval round-trip for every action.
  4. Return block explanations to the parent agent, then rerun unstable cases until flapping disappears so the reviewer rarely interrupts the user directly.

**Try today:** Label 50 real agent actions from your own repo, add 10 synthetic 'read secret or touch prod' cases, and see whether a small reviewer can narrow the action instead of asking a human.

### Make every agent task bootable in its own worktree with its own logs and traces

**Why:** Agents validate faster when each task gets a self-contained app instance and local observability instead of fighting shared state or asking humans to reproduce bugs.

**Benefit:** both | **Setup:** hours | **Grade:** A

**Evidence:** OpenAI says the product was built in about one-tenth the hand-written time, reached roughly 1,500 merged PRs at about 3.5 PRs per engineer per day, and regularly lets Codex work on a single task for six hours while using per-worktree app and observability instances.

**Source:** https://openai.com/index/harness-engineering/

**How-to:** https://openai.com/index/harness-engineering/

**Steps:**
  1. Make the app bootable from any git worktree or branch so each agent can launch an isolated runtime for just the code it is changing.
  2. Expose browser-driving or CDP-style tooling plus screenshots or DOM snapshots so the agent can reproduce and validate UI behavior directly inside that worktree.
  3. Attach an ephemeral local observability stack to the worktree and teach agents the query surface for logs, metrics, and traces so they can inspect their own runs.
  4. Tear the per-task runtime down when the work ends so the next task starts from a clean state rather than inheriting another agent's leftovers.

**Try today:** Pick one service, make it boot from a fresh worktree with an isolated log stream, and have the agent reproduce one bug without touching your shared dev stack.

## All findings by lens

### build-robust
- [Put a contextual reviewer in front of risky agent actions](https://cursor.com/blog/agent-autonomy-auto-review) (ai-driven-development)
- [Audit coding benchmarks with investigator agents before you trust the score](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) (ai-development)

### model-workflows
- [Defer tool loading so agents search for tools instead of hauling them into every prompt](https://www.anthropic.com/engineering/advanced-tool-use) (ai-development)

### ship-faster
- [Split long agent projects into recursive planners and isolated workers](https://cursor.com/blog/scaling-agents) (ai-driven-development)

### tooling-setups
- [Make every agent task bootable in its own worktree with its own logs and traces](https://openai.com/index/harness-engineering/) (ai-driven-development)

