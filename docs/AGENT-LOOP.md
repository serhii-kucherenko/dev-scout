# Agent loop

Chat-driven Ralph-style loop. Full details: [CHAT-LOOP.md](CHAT-LOOP.md).

1. User starts chat in Cursor with kickoff prompt (see README)
2. Agent writes `GOAL.md` and runs research stages as file writes
3. Agent judges sufficiency via `config/judge.yaml`
4. If gaps → `feedback-NNN.md` → re-research
5. If pass → digest + email draft

No terminal commands required.
