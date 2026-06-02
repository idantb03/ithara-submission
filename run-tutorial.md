# Run tutorial — Ithara Booking Bot

Step-by-step guide to run the WhatsApp booking automation service locally in **demo mode** (no real WhatsApp, Ithara API, or email credentials required).

Run all commands from the **repository root** (`ithara-booking-bot/`), not from `ithara-booking-bot-working-ref/` (that folder is a local comparison copy only).

---

## Prerequisites

- **Python 3.11+** (matches the [Dockerfile](Dockerfile))
- `pip` (bundled with Python)
- Optional: [curl](https://curl.se/) or PowerShell 5.1+ for webhook tests

---

## 1. Setup

### Create a virtual environment (recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Configure environment

```powershell
Copy-Item .env.example .env
```

By default, `.env` has `DEMO_MODE=true`. No API keys are required for local demo.

---

## 2. Start the API

```powershell
python -m uvicorn main:app --reload --port 8000
```

You should see Uvicorn listening on `http://127.0.0.1:8000`.

---

## 3. Smoke checks

### Health endpoint

**PowerShell:**

```powershell
Invoke-RestMethod http://localhost:8000/health
```

**curl:**

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "healthy", "demo_mode": true}
```

### Meta webhook verification (optional)

When connecting to Meta WhatsApp Cloud API, Meta sends a GET to verify your webhook:

```
GET /webhook/whatsapp?hub.mode=subscribe&hub.challenge=CHALLENGE&hub.verify_token=ithara_webhook_verify
```

If `hub.verify_token` matches `WHATSAPP_VERIFY_TOKEN` in `.env` (default: `ithara_webhook_verify`), the server returns the challenge integer.

---

## 4. Simulate a booking (happy path)

With the server running, send a test WhatsApp webhook payload.

### PowerShell

```powershell
$body = @{
  entry = @(
    @{
      changes = @(
        @{
          value = @{
            messages = @(
              @{
                from = "971501234567"
                type = "text"
                text = @{ body = "Hi I want to book ITH-A1B2-C3D4 for this Friday" }
                timestamp = "1716800000"
              }
            )
            contacts = @(
              @{ profile = @{ name = "Sarah Mitchell" }; wa_id = "971501234567" }
            )
          }
        }
      )
    }
  )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method POST -Uri http://localhost:8000/webhook/whatsapp `
  -ContentType "application/json" -Body $body
```

### curl

```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "971501234567",
            "type": "text",
            "text": {"body": "Hi I want to book ITH-A1B2-C3D4 for this Friday"},
            "timestamp": "1716800000"
          }],
          "contacts": [{"profile": {"name": "Sarah Mitchell"}, "wa_id": "971501234567"}]
        }
      }]
    }]
  }'
```

This matches the sample in [`mock/webhook_payload.py`](mock/webhook_payload.py).

### What you should see

In the **Uvicorn terminal** (not the client), demo mode prints outbound messages instead of sending them:

```
[DEMO] WhatsApp -> 971501234567:
Booking Confirmed!
...

[DEMO] Email -> bookings@sofitel-example.com
Subject: New Ithara Booking - ...
```

The HTTP response is immediate: `{"status":"ok"}`. The booking pipeline runs in the background.

---

## 5. Test voucher codes

Use these codes in the `text.body` field when simulating webhooks:

| Code | Expected result |
|------|-----------------|
| `ITH-A1B2-C3D4` | Valid — Relaxing Spa Day (Sofitel Dubai) |
| `ITH-B5C6-D7E8` | Valid — Desert Safari |
| `ITH-X1Y2-Z3W4` | Expired |
| `ITH-R3D4-E5M5` | Already redeemed |

---

## 6. Extra scenarios

Change only the message `body` in the payload above.

| Message body | Expected behavior |
|--------------|-------------------|
| `I want to redeem my voucher ITH-A1B2-C3D4` | Asks customer for preferred date |
| `hello` | Prompts for voucher code and date |
| `I have a problem with my voucher` | Support path — ops email + customer acknowledgment |

---

## 7. Run tests

From the repo root (with venv active):

```powershell
python -m pytest -q
```

Expected: **10 passed**.

Verbose output:

```powershell
python -m pytest tests/ -v
```

---

## 8. Docker (optional)

Build and run:

```powershell
docker build -t ithara-booking-bot .
docker run -p 8000:8000 --env-file .env ithara-booking-bot
```

Then check health:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

---

## 9. Going to production

Set `DEMO_MODE=false` in `.env` and configure:

- `WHATSAPP_PHONE_ID`, `WHATSAPP_TOKEN`, `WHATSAPP_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN`
- `ITHARA_API_BASE`, `ITHARA_API_KEY`
- `SMTP_*`, `OPS_EMAIL`, `FROM_EMAIL`

In production mode:

- Outbound WhatsApp and email use real APIs
- `POST /webhook/whatsapp` requires a valid `X-Hub-Signature-256` header

See the [README.md](README.md) production checklist for deployment notes.

---

## Known limitations

- **Multi-turn conversations are not persisted.** Each webhook is handled independently. If a customer sends a voucher in one message and a date in a later message, the second message will not automatically continue the first booking flow.
- **`SESSION_DB_URL`** is reserved for future session support; the pipeline does not use it yet.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Activate venv and run `pip install -r requirements.txt` |
| No `[DEMO]` output after POST | Check the Uvicorn terminal (pipeline is async) |
| Port 8000 in use | Use `--port 8001` or stop the other process |
| Tests fail on import | Run pytest from repo root, not `working-ref/` |
