# Delivery

Agent writes output files in chat after judge pass:

- `05-report/daily-digest.md` — full jam cookbook
- `06-email/email-draft.md` — scannable brief with To/Subject headers
- `06-email/email-draft.json` — structured draft
- `06-email/email-draft.eml` — open/import in a mail client

Tell the user where to read the draft. **No email API keys** — no Resend, no SMTP. The markdown/eml files are the delivery.

Optional: user forwards the draft manually from their own mail client.
