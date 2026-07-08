# Judge

Agent checks research in chat before writing digest or email.

## Checks (`config/judge.yaml`)

- ≥5 promotable JamItems (grade A/B, source + steps)
- ≥2 corroborated items
- ≥3 lenses with findings
- No fluff keywords without evidence

## Agent writes

- `04-judge/verdict.json` — `{ "sufficient": true|false, "gaps": [...] }`
- `04-judge/gaps.md` if fail

If insufficient → `feedback-NNN.md` from `templates/feedback.md` → re-research.

**Never** write `05-report/` or `06-email/` until sufficient.
