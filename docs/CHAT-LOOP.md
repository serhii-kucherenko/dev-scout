# Chat loop — how to run Dev Scout in Cursor

No CLI. No API keys. Open this repo in Cursor and drive the loop from chat.

## Kickoff prompts (copy into chat)

**Start a new day:**

```
Run today's dev scout research loop.
Read AGENTS.md and docs/CHAT-LOOP.md first.
Find practical ways to ship faster and build more robust software with AI-assisted dev.
Deliver jam with source links and how-tos when judge passes.
```

**Continue an in-progress day:**

```
Continue the dev scout loop for runs/YYYY-MM-DD/.
Read RUN.md and any feedback-*.md, then pick up where we left off.
```

**Re-research after thin results:**

```
The dev scout judge failed for runs/YYYY-MM-DD/.
Read gaps.md and feedback files, re-research the gaps, then update judge and outputs.
```

---

## Loop stages (agent writes these files)

| Stage | What the agent does | Artifacts |
|-------|---------------------|-----------|
| 1. Intake | Copy `templates/GOAL.md` → `runs/YYYY-MM-DD/GOAL.md`, check `data/findings.json` | `00-intake/intake.json` |
| 2. Discover | Search web per playbook + `config/sources.yaml` | `01-research/discover/fetch-plan.json`, `source-discovery.json` |
| 3. Collect | Fetch URLs, save excerpts | `01-research/excerpts.jsonl`, optional `raw/` |
| 4. Lenses | Analyze excerpts per `config/lenses/` | `01-research/lenses/<id>/output.json` |
| 5. Corroborate | Verify claims with second sources | `01-research/corroboration.json` |
| 6. Coverage | Summarize research health | `01-research/coverage.json` |
| 7. Judge | Check `config/judge.yaml` | `04-judge/verdict.json`, `gaps.md` if fail |
| 8. Output | Only if judge passes; put `To: $DEV_SCOUT_EMAIL` on the draft | `05-report/daily-digest.md`, `06-email/email-draft.md` (+ `.json` / `.eml`) |
| 9. Learn | Dedupe into ledger | `07-learning/delta-vs-last-day.json`, update `data/findings.json` |

Update `RUN.md` after each stage so the next chat session can resume.

---

## If judge fails

1. Write `feedback-NNN.md` with specific gaps (missing lenses, weak corroboration, no how-tos)
2. Re-run discover/collect scoped to gaps
3. Do **not** write email or digest until `verdict.json` has `"sufficient": true`

---

## Discovery tools (subscriptions only)

**No API keys.** Use:

| Tool | For |
|------|-----|
| **Cursor web search** | Broad discovery |
| **agent-reach** | Twitter, Reddit, HN, GitHub, articles |
| **`gh search`** | GitHub repos/releases (if `gh auth` exists) |
| **Web fetch** | Primary sources from fetch plan |

See [SUBSCRIPTIONS.md](SUBSCRIPTIONS.md) and [DISCOVERY-PLAYBOOK.md](DISCOVERY-PLAYBOOK.md).

Do **not** ask the user for OpenAI, Anthropic, Exa, or Resend keys.

Respect `config/governance/data-boundaries.yaml`.

---

## JamItem shape

Each finding in lens `output.json` and `03-rank/ranked.json`:

```json
{
  "id": "ship-faster-1",
  "title": "...",
  "why": "...",
  "benefit": "speed",
  "source_url": "https://...",
  "how_to_url": "https://...",
  "how_to_steps": ["step 1", "step 2", "step 3"],
  "setup_cost": "hours",
  "evidence": "2x PR velocity",
  "evidence_grade": "A",
  "lens_id": "ship-faster",
  "corroboration": "supported",
  "try_today": "One concrete first action"
}
```

See `templates/jam-item.example.json`.

---

## Optional Python helpers

The `src/dev_scout/` package exists for CI smoke tests only. **Users and agents should not need it.** Prefer writing files directly in chat.
