# Dev Scout Daily Digest — 2026-07-12

Actionable jam for faster, more robust development.

Repo: https://github.com/serhii-kucherenko/dev-scout

## Building AI systems

Practices for designing, testing, deploying, and operating AI systems.

### Separate guaranteed resources from kill limits in agentic evals

**Why:** Benchmark scores move when containers are OOM-killed for transient spikes, so resource policy needs to be part of the eval design.

**Benefit:** robustness | **Setup:** hours | **Grade:** A

**Evidence:** Anthropic reports a 6-point spread on Terminal-Bench 2.0 between the strictest and most generous setups; a 3x ceiling cut infra errors from 5.8% to 2.1% while keeping score lift within noise.

**Source:** https://www.anthropic.com/engineering/infrastructure-noise

**How-to:** https://www.anthropic.com/engineering/infrastructure-noise

**Steps:**
  1. Publish both the guaranteed allocation and the hard kill threshold for each task instead of a single exact resource number.
  2. Calibrate headroom by rerunning the eval at several ceilings and find the smallest band where score changes stay within noise while infrastructure failures drop.
  3. Report infra error rate, time limits, and concurrency alongside pass rate so consumers can judge whether the setup is stable.
  4. Treat small leaderboard deltas as suspect until the resource methodology matches across runs.

**Try today:** Re-run one coding eval with separate floor and ceiling settings and log how much of today's failure rate is infrastructure rather than model behavior.


### Keep session, harness, and sandboxes separate in long-running agents

**Why:** Decoupling the brain from the session log and execution hands makes agents recoverable, faster to start, and easier to secure.

**Benefit:** both | **Setup:** hours | **Grade:** A

**Evidence:** Anthropic says decoupling brain from hands cut p50 time-to-first-token by roughly 60% and p95 by over 90% while improving recoverability and secret isolation.

**Source:** https://www.anthropic.com/engineering/managed-agents

**How-to:** https://www.anthropic.com/engineering/managed-agents

**Steps:**
  1. Move the durable session log out of the sandbox so a crashed harness can be restarted from recorded events instead of losing the run.
  2. Run the harness outside the execution environment and reach sandboxes or tools through a narrow execute-style interface.
  3. Provision a sandbox only when a task actually needs one so inference can start before repo clone or container setup finishes.
  4. Keep secrets outside the sandbox and expose external systems through scoped repo credentials, proxies, or vault-backed tools.

**Try today:** Take one long-running agent loop, split its event log out of the worker container, and measure startup latency before and after.


### Let production agents act only inside an approved plan

**Why:** Production agents need least-privilege changes that are scoped to one plan, not standing access that lives for the whole session.

**Benefit:** robustness | **Setup:** hours | **Grade:** B

**Evidence:** Vercel says its agent traced a bad deploy, recommended rollback, and mitigated the incident in under three minutes; the same system is read-only by default and verifies generated fixes in Sandbox before surfacing them.

**Source:** https://vercel.com/blog/vercel-agent

**How-to:** https://vercel.com/blog/vercel-agent

**Steps:**
  1. Run the agent under its own service identity so every action is attributable and does not automatically inherit a human's full access.
  2. Keep the agent read-only by default and require it to propose a concrete plan before it can roll back, change config, or touch production.
  3. Mint short-lived capabilities only for the tasks named in that approved plan, then drop the agent back to read-only when the plan ends.
  4. Execute generated fixes inside an isolated sandbox against the real project build, tests, and linters before surfacing a PR or rollback recommendation.

**Try today:** Take the highest-risk agent in your stack, force it into read-only mode by default, and make every write path go through a single approved-plan capability grant.


### Make tiered reasoning the default model policy

**Why:** A Sol/Terra/Luna ladder keeps routine coding cheap and fast while reserving max and ultra for work that truly benefits from more compute and more agents.

**Benefit:** both | **Setup:** hours | **Grade:** A

**Evidence:** OpenAI says GPT-5.6 Sol reaches 80 on the Artificial Analysis Coding Agent Index, 2.8 points above Claude Fable 5 at about one-third lower cost; Terra performs just above Fable 5 and Luna beats Opus 4.8 at about one-quarter the estimated cost, while ultra coordinates four agents in parallel by default.

**Source:** https://openai.com/index/gpt-5-6/

**How-to:** https://openai.com/index/gpt-5-6/

**Steps:**
  1. Default routine implementation, search, and refactor tasks to the cheaper tier that still clears your quality bar, such as Terra or Luna.
  2. Escalate only stalled or high-stakes tasks to Sol with max reasoning, and reserve ultra or multi-agent mode for long-horizon work where faster time-to-result matters.
  3. Log solve rate, latency, tool-call volume, and token cost by task class so escalation rules are based on evidence instead of instinct.
  4. Use prompt caching and programmatic tool calling when the workflow repeatedly resends the same context or processes large intermediate outputs.

**Try today:** Pick one coding workflow, route the happy path to Terra, escalate only retries to Sol max, and compare solve rate plus cost over the next day.


## Using AI to build software

Practices for faster, safer everyday development with AI coding assistants.

### Measure review agents by resolved bugs, not comment volume

**Why:** Resolved-bug rate gives review agents a quality target tied to real fixes instead of noisy comment counts.

**Benefit:** both | **Setup:** hours | **Grade:** A

**Evidence:** Cursor says 40 experiments raised Bugbot's resolution rate from 52% to over 70% and increased resolved bugs per PR from roughly 0.2 to about 0.5, while Bugbot now reviews more than two million PRs per month.

**Source:** https://cursor.com/blog/building-bugbot

**How-to:** https://cursor.com/blog/building-bugbot

**Steps:**
  1. Run several review passes in parallel with different diff orderings so the agent explores multiple bug hypotheses.
  2. Cluster overlapping findings, keep only issues confirmed by majority voting, and pass the survivors through a validator model before posting.
  3. At merge time, measure which reported bugs were actually fixed in the final code and treat that resolution rate as the main quality metric.
  4. Hill-climb prompts, tools, and filters against resolved-bugs-per-PR instead of raw comment volume.

**Try today:** Take one review agent, add a post-merge “was this actually fixed?” audit, and compare resolved bugs per PR before changing anything else.


## All findings by lens

### build-robust
- [Separate guaranteed resources from kill limits in agentic evals](https://www.anthropic.com/engineering/infrastructure-noise) (ai-development)

### model-workflows
- [Make tiered reasoning the default model policy](https://openai.com/index/gpt-5-6/) (ai-development)

### production-patterns
- [Keep session, harness, and sandboxes separate in long-running agents](https://www.anthropic.com/engineering/managed-agents) (ai-development)
- [Let production agents act only inside an approved plan](https://vercel.com/blog/vercel-agent) (ai-development)

### ship-faster
- [Measure review agents by resolved bugs, not comment volume](https://cursor.com/blog/building-bugbot) (ai-driven-development)
