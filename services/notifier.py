from email.mime.text import MIMEText

import aiosmtplib
import httpx

from config import settings

WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_ID}/messages"
HEADERS = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}", "Content-Type": "application/json"}


async def send_whatsapp(phone: str, message: str) -> bool:
    if settings.DEMO_MODE:
        print(f"\n[DEMO] WhatsApp -> {phone}:\n{message}\n")
        return True

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message},
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(WHATSAPP_API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            return True
        except Exception as exc:
            print(f"WhatsApp send failed: {exc}")
            return False


async def send_email(to: str, subject: str, body: str) -> bool:
    if settings.DEMO_MODE:
        print(f"\n[DEMO] Email -> {to}\nSubject: {subject}\n{body}\n")
        return True
    msg = MIMEText(body)
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    try:
        async with aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT) as smtp:
            await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            await smtp.send_message(msg)
        return True
    except Exception as exc:
        print(f"Email send failed: {exc}")
        return False


def booking_confirmed_msg(name: str, experience: str, date: str, time: str, partner: str, code: str, notes: str) -> str:
    return (
        f"Booking Confirmed!\n\n"
        f"Hi {name}! Your experience is all set.\n\n"
        f"Experience: {experience}\n"
        f"Date: {date}\n"
        f"Time: {time}\n"
        f"Venue: {partner}\n"
        f"Voucher: {code}\n\n"
        f"{notes}\n\n"
        f"Enjoy your experience! - The Ithara Team"
    )


def ask_for_date_msg(name: str, experience: str) -> str:
    return (
        f"Hi {name}! I found your voucher for {experience}.\n\n"
        "To book your experience, please reply with your preferred date and time.\n\n"
        "For example: Friday 30 May, morning or next weekend, afternoon."
    )


def voucher_problem_msg(error_message: str) -> str:
    return (
        f"I couldn't find a valid voucher with that code. {error_message}\n\n"
        "Please check your voucher email or visit enjoy.ithara.ae for help. "
        "You can also reply here and our team will assist you."
    )


def ops_handoff_email(
    customer_name: str,
    phone: str,
    message: str,
    voucher_code: str,
    experience: str,
    partner: str,
    preferred_date: str,
    reason: str,
) -> str:
    return (
        "Manual booking needed.\n\n"
        f"Customer: {customer_name}\n"
        f"Phone: {phone}\n"
        f"Original message: {message}\n\n"
        f"Voucher: {voucher_code}\n"
        f"Experience: {experience}\n"
        f"Partner: {partner}\n"
        f"Preferred date: {preferred_date or 'Not specified'}\n\n"
        f"Reason for escalation: {reason}\n\n"
        "---\nAll context pre-filled. Please contact the partner and confirm directly."
    )


def ops_handoff_msg(name: str) -> str:
    return (
        f"Hi {name}! We are confirming availability with the venue and our team "
        "will follow up within a few hours. Thank you for your patience! - Ithara Team"
    )
