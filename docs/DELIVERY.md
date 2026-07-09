# Delivery

After judge pass, Dev Scout:

1. Writes the findings brief under `runs/YYYY-MM-DD/06-email/`
2. **Emails that brief to `DEV_SCOUT_EMAIL`** via Resend

## What each email contains

Emails are kept **scannable** — full steps and evidence live in the digest.

1. **Repo link** — every brief links back to the project repo (`repo_url` in `config/delivery.yaml`, or `DEV_SCOUT_REPO_URL`)
2. **Quick review of the previous email** — titles, benefits, and source links from the last brief (or “first brief” if none), so you can jump straight back into a topic
3. **New since last brief** — findings whose source was not already emailed or stored in `data/findings.json`. Each is one compact block:
   - title with a tag line — `benefit · setup effort · evidence grade` so you can decide at a glance whether it's worth a look
   - **Why it matters** — one line on what it's for
   - **Try** — one concrete first step (when available)
   - **Link** — the source URL
4. **Recap** — if there is little new jam, a short list of recent findings still worth a look, so a brief is never just one line
5. Link to the **full digest** for every step, evidence, corroboration, and lens

Artifacts still written locally:

- `05-report/daily-digest.md` — full jam cookbook
- `06-email/email-draft.md` — scannable brief with To/Subject headers
- `06-email/email-draft.json` — structured draft (`new_count`, `previous_day`, `top_items`)
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
