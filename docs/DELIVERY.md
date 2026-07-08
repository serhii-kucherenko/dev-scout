# Delivery

Output layer only — runs after judge pass.

## Draft mode (default)

Writes `06-email/email-draft.md` and `email-draft.json`.

## Send mode

Set `config/delivery.yaml`:

```yaml
mode: send
```

Requires `RESEND_API_KEY` and `DELIVERY_FROM` in `.env`.

```bash
dev-scout compose-email
dev-scout send --dry-run
dev-scout send
```
