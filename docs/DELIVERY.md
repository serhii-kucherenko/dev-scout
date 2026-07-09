# Delivery

After judge pass, Dev Scout:

1. Writes the findings brief under `runs/YYYY-MM-DD/06-email/`
2. **Emails that brief to `DEV_SCOUT_EMAIL`** via Resend

Artifacts still written locally:

- `05-report/daily-digest.md` — full jam cookbook
- `06-email/email-draft.md` — scannable brief with To/Subject headers
- `06-email/email-draft.json` — structured draft
- `06-email/email-draft.eml` — open/import in a mail client
- `06-email/send-result.json` — send status (`sent`, `skipped`, or `error`)

## GitHub secrets / env

Add these in GitHub → Settings → Secrets and variables → Actions:

| Name | Purpose |
|------|---------|
| `DEV_SCOUT_EMAIL` | Recipient of the findings report |
| `RESEND_API_KEY` | Resend API key |
| `DELIVERY_FROM` | Verified From address (e.g. `Dev Scout <onboarding@resend.dev>`) |

Locally, copy `.env.example` → `.env` and fill the same values.

Without `RESEND_API_KEY` / `DELIVERY_FROM`, the pipeline still writes drafts and records `send-result.json` as skipped — it does not fail the research run.

## Chat loop

After judge pass, the agent writes the draft files. If the Python harness is available with the secrets above, run send (or the full `day` pipeline) so the report is emailed. Otherwise commit the draft and send from CI / a machine that has the secrets.
