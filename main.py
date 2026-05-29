import asyncio
import hashlib
import hmac

from fastapi import FastAPI, HTTPException, Query, Request

from config import settings
from models.message import WhatsAppMessage
from pipeline import run

app = FastAPI(title="Ithara Booking Automation", version="1.0.0")


@app.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
):
    """Meta webhook verification handshake."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/whatsapp")
async def receive_message(request: Request):
    """Receives incoming WhatsApp messages and runs the booking pipeline."""
    body_bytes = await request.body()
    if not settings.DEMO_MODE:
        _verify_signature(body_bytes, request.headers.get("X-Hub-Signature-256", ""))

    payload = await request.json()
    try:
        entry = payload["entry"][0]["changes"][0]["value"]
        messages = entry.get("messages", [])
        if not messages:
            return {"status": "ok", "note": "no messages in payload"}
        if messages[0].get("type") != "text":
            return {"status": "ok", "note": "non-text message ignored"}

        raw_msg = WhatsAppMessage(
            phone=messages[0]["from"],
            customer_name=entry["contacts"][0]["profile"]["name"],
            body=messages[0]["text"]["body"],
            received_at=str(messages[0]["timestamp"]),
        )
    except (KeyError, IndexError):
        return {"status": "ok", "note": "unrecognised payload shape"}

    asyncio.create_task(run(raw_msg))
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy", "demo_mode": settings.DEMO_MODE}


def _verify_signature(body: bytes, header: str) -> None:
    expected = "sha256=" + hmac.new(settings.WHATSAPP_APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, header):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")
