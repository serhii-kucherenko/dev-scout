To: kucherenko.web@gmail.com
Subject: Dev Scout 2026-W28 - 5 ways to ship faster and build safer

Dev Scout - 2026-W28

This week's jam is about moving review earlier, routing to cheaper default models, and hardening agent systems before they reach prod.

1. Run Bugbot before you push (both)
   Why: Move review left so the same agent catches bugs on the diff before the PR roundtrip starts.
   Evidence: Cursor says Bugbot is over 3x faster, 22% cheaper, finds 10% more bugs per review, and 90% of runs now finish in under 3 minutes.
   Source: https://cursor.com/blog/bugbot-updates-june-2026
   Try Monday: Enable Bugbot on one active repo and require its check on draft PRs for one week.

2. Make GPT-5 mini the default coding workhorse (both)
   Why: A cheap high-skill default model lets teams save the expensive model for cases where verification says more horsepower is actually needed.
   Evidence: OpenAI reports GPT-5 mini scores 71.0% on SWE-bench Verified and 71.6% on Aider polyglot while costing $0.25 per 1M input tokens and $2 per 1M output tokens.
   Source: https://openai.com/index/introducing-gpt-5-for-developers/
   Try Monday: Change one editor or agent default to GPT-5 mini and keep a simple escalation rule when verification fails.

3. Treat system-prompt edits like code changes (robustness)
   Why: Prompt tweaks can silently degrade code quality, so they need the same gating discipline as production code.
   Evidence: Anthropic reports that one verbosity instruction caused a 3% drop on both Opus 4.6 and 4.7 in a broader evaluation set, and it immediately reverted the change.
   Source: https://www.anthropic.com/engineering/april-23-postmortem
   Try Monday: Put your agent prompt under version control and block merges unless the change passes both narrow and broad eval suites.

4. Design containment at the environment layer first (robustness)
   Why: Sandbox and egress boundaries keep failures bounded even when the model, a tool, or a user prompt goes off the rails.
   Evidence: Anthropic says its Claude Code sandbox cut permission prompts by 84%, auto mode catches about 83% of overeager behaviors, and Gray Swan prompt-injection success is roughly 0.1% on single attempts.
   Source: https://www.anthropic.com/engineering/how-we-contain-claude
   Try Monday: Move one internal coding agent into a workspace-only sandbox with network denied by default and audit what access it still truly needs.

5. Use always-on cloud agents for review, triage, and incident chores (both)
   Why: Background automations keep review and maintenance work moving without waiting for someone to open the IDE.
   Evidence: Cursor says Bugbot-like automations run thousands of times a day and have caught millions of bugs; its internal security-review automation has caught multiple vulnerabilities and critical bugs; Runlayer says the setup helps them move faster than teams five times their size.
   Source: https://cursor.com/blog/automations
   Try Monday: Ship one cron or PR-open automation that reviews merged code for missing tests and posts only high-confidence findings.

Full detail: runs/2026-W28/05-report/weekly-digest.md
