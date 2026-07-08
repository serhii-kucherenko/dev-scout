# Agent loop

Ralph-style outer loop until research is sufficient.

1. Write `GOAL.md` with research questions and sufficiency criteria
2. `dev-scout discover`
3. `dev-scout collect`
4. `dev-scout lens --all`
5. `dev-scout corroborate`
6. `dev-scout judge --json`
7. If gaps → `feedback-001.md` → repeat 2–6 scoped to gaps
8. `dev-scout report` + `dev-scout compose-email`

Or use `dev-scout loop --goal-file GOAL.md` for automated iterations (max 3 by default).
