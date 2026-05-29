import re
from typing import Any

from config import settings
from models.message import ParsedMessage, WhatsAppMessage

BOOKING_KEYWORDS = re.compile(r"\b(book|redeem|voucher|schedule|reserve|appointment|slot|date|use)\b", re.I)
SUPPORT_KEYWORDS = re.compile(r"\b(problem|issue|expired|wrong|cancel|refund|complaint|broken|error)\b", re.I)
AVAILABILITY_KEYWORDS = re.compile(r"\b(available|availability|open|free|when can|check)\b", re.I)
VOUCHER_PATTERN = re.compile(r"\b(ITH-[A-Z0-9]{4}-[A-Z0-9]{4}|[A-Z0-9]{8})\b", re.I)
DATE_PATTERNS = [
    re.compile(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I),
    re.compile(r"\b(today|tomorrow|this weekend|next week|next weekend)\b", re.I),
    re.compile(r"\b(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)\b"),
    re.compile(r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)\b", re.I),
]


def classify_keyword(body: str) -> str:
    if SUPPORT_KEYWORDS.search(body):
        return "support"
    if BOOKING_KEYWORDS.search(body):
        return "booking"
    if AVAILABILITY_KEYWORDS.search(body):
        return "availability"
    return "unknown"


def extract_voucher_code(body: str) -> str | None:
    match = VOUCHER_PATTERN.search(body)
    return match.group(1).upper() if match else None


def extract_date(body: str) -> str | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(body)
        if match:
            return match.group(0)
    return None


async def classify_claude(body: str) -> dict[str, Any]:
    import json
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompt = f"""Classify this WhatsApp message from an Ithara.ae experience voucher customer.

Message: "{body}"

Reply ONLY with a JSON object. No preamble, no markdown, no explanation. Only JSON.
{{
  "intent": "booking" | "support" | "availability" | "unknown",
  "voucher_code": "<extracted code or null>",
  "preferred_date": "<extracted date string or null>"
}}"""

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.content[0].text)
    except Exception:
        return {
            "intent": classify_keyword(body),
            "voucher_code": extract_voucher_code(body),
            "preferred_date": extract_date(body),
        }


async def parse_message(msg: WhatsAppMessage) -> ParsedMessage:
    body = msg.body
    if settings.USE_CLAUDE_CLASSIFIER and settings.ANTHROPIC_API_KEY:
        result = await classify_claude(body)
        intent = result.get("intent", "unknown")
        voucher_code = result.get("voucher_code")
        preferred_date = result.get("preferred_date")
    else:
        intent = classify_keyword(body)
        voucher_code = extract_voucher_code(body)
        preferred_date = extract_date(body)

    return ParsedMessage(
        **msg.model_dump(),
        intent=intent,
        voucher_code=voucher_code,
        preferred_date=preferred_date,
        needs_date_collection=(intent == "booking" and preferred_date is None),
    )
