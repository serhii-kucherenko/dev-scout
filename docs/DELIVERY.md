# Delivery

After judge pass, the agent writes:

- `05-report/daily-digest.md` — full jam cookbook
- `06-email/email-draft.md` — scannable brief with To/Subject headers
- `06-email/email-draft.json` — structured draft
- `06-email/email-draft.eml` — open/import in a mail client

## Recipient (`To:`)

Set your address with **`DEV_SCOUT_EMAIL`** (preferred) or `DELIVERY_TO`.

1. Add `DEV_SCOUT_EMAIL` in GitHub → Settings → Secrets and variables → Actions
2. Or put it in a local `.env` (see `.env.example`)

Drafts use that value in the `To:` header. Config `recipient` in `config/delivery.yaml` is only a fallback when the env var is unset.

**No Resend/SMTP keys are required** for draft mode — the markdown/eml files are the delivery. Optional send via Resend remains behind `delivery.mode: send` plus `RESEND_API_KEY` and `DELIVERY_FROM`.
