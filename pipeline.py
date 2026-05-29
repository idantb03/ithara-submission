from models.message import WhatsAppMessage
from services.availability import check_availability
from services.booking import create_booking
from services.intent import parse_message
from services.notifier import (
    ask_for_date_msg,
    booking_confirmed_msg,
    ops_handoff_email,
    ops_handoff_msg,
    send_email,
    send_whatsapp,
    voucher_problem_msg,
)
from services.voucher import validate_voucher
from config import settings


async def run(raw_msg: WhatsAppMessage) -> None:
    msg = await parse_message(raw_msg)

    if msg.intent == "support":
        await _handle_support(msg)
        return

    if msg.intent != "booking":
        await send_whatsapp(
            msg.phone,
            "Hi! I'm here to help with your Ithara experience booking. "
            "Please share your voucher code (e.g. ITH-XXXX-XXXX) and preferred date.",
        )
        return

    if not msg.voucher_code:
        await send_whatsapp(
            msg.phone,
            "I'd love to help you book! Please share your voucher code "
            "(it looks like ITH-XXXX-XXXX) and I'll get started.",
        )
        return

    voucher = await validate_voucher(msg.voucher_code)
    if not voucher.valid:
        await send_whatsapp(msg.phone, voucher_problem_msg(voucher.message or ""))
        return

    if msg.needs_date_collection:
        await send_whatsapp(msg.phone, ask_for_date_msg(msg.customer_name, voucher.experience or "your experience"))
        return

    availability = await check_availability(voucher, msg.preferred_date or "")
    if not availability.available:
        await send_email(
            to=settings.OPS_EMAIL,
            subject=f"Manual booking needed - {msg.customer_name} ({msg.phone})",
            body=ops_handoff_email(
                customer_name=msg.customer_name,
                phone=msg.phone,
                message=msg.body,
                voucher_code=msg.voucher_code,
                experience=voucher.experience or "Unknown experience",
                partner=voucher.partner_name or "Unknown partner",
                preferred_date=msg.preferred_date or "",
                reason=availability.fail_reason or "Partner did not confirm",
            ),
        )
        await send_whatsapp(msg.phone, ops_handoff_msg(msg.customer_name))
        return

    booking = await create_booking(
        voucher=voucher,
        customer_phone=msg.phone,
        customer_name=msg.customer_name,
        confirmed_date=availability.confirmed_date or msg.preferred_date or "",
        confirmed_time=availability.confirmed_time or "TBD",
    )

    await send_whatsapp(
        msg.phone,
        booking_confirmed_msg(
            name=msg.customer_name,
            experience=voucher.experience or "Experience",
            date=booking.booking_date,
            time=booking.booking_time,
            partner=voucher.partner_name or "Partner venue",
            code=msg.voucher_code,
            notes=availability.notes or "",
        ),
    )

    await send_email(
        to=voucher.partner_email or settings.OPS_EMAIL,
        subject=f"New Ithara Booking - {voucher.experience} - {booking.booking_date}",
        body=(
            "New Booking Confirmation\n\n"
            f"Experience: {voucher.experience}\n"
            f"Date: {booking.booking_date}\n"
            f"Time: {booking.booking_time}\n\n"
            f"Customer: {msg.customer_name}\n"
            f"Voucher: {msg.voucher_code}\n"
            f"Customer Contact: {msg.phone}\n\n"
            "Please reply to confirm receipt.\n- Ithara Operations Team"
        ),
    )


async def _handle_support(msg: WhatsAppMessage) -> None:
    await send_email(
        to=settings.OPS_EMAIL,
        subject=f"Support request via WhatsApp - {msg.customer_name}",
        body=f"Customer: {msg.customer_name}\nPhone: {msg.phone}\nMessage: {msg.body}",
    )
    await send_whatsapp(
        msg.phone,
        f"Hi {msg.customer_name}! Thanks for reaching out. "
        "Our team has received your message and will get back to you shortly. - Ithara Team",
    )
