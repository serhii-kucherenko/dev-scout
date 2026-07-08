# Delivery

Agent writes output files after judge pass:

- `05-report/weekly-digest.md` — full jam cookbook
- `06-email/email-draft.md` — scannable brief for the user
- `06-email/email-draft.json` — structured copy (optional)

Email structure: see [CHAT-LOOP.md](CHAT-LOOP.md).

Tell the user where to read the draft. No send automation required in v1 — user copies from markdown or requests send in a follow-up chat.

Optional: `config/delivery.yaml` for future email integration.
