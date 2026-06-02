# Ithara Booking Bot (Build 2b)

FastAPI-based WhatsApp booking automation service for voucher redemption flow.

**Full local walkthrough → [run-tutorial.md](run-tutorial.md)**

## Quick start

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn main:app --reload --port 8000
```

See [run-tutorial.md](run-tutorial.md) for webhook simulation, test vouchers, pytest, and Docker.

## Endpoints

- `GET /health`
- `GET /webhook/whatsapp` (Meta verification)
- `POST /webhook/whatsapp` (incoming WhatsApp payload)

## Demo vs Production toggle

- `DEMO_MODE=true`:
  - Uses local mock voucher/availability data
  - Prints WhatsApp/email outputs to console
  - Skips webhook signature verification
- `DEMO_MODE=false`:
  - Uses live API/email paths
  - Enforces `X-Hub-Signature-256` verification

## Production checklist

- Set all required env vars (`WHATSAPP_*`, `ITHARA_*`, `SMTP_*`, `OPS_EMAIL`, `FROM_EMAIL`)
- Set `DEMO_MODE=false`
- Optionally set `USE_CLAUDE_CLASSIFIER=true` with `ANTHROPIC_API_KEY`
- Deploy with Docker/App Runner and health check path `GET /health`

Note: `SESSION_DB_URL` is reserved for future multi-turn sessions; the pipeline does not use it yet.

## Tests

10 tests (intent, voucher validation, pipeline). From the repo root:

```powershell
python -m pytest -q
```
