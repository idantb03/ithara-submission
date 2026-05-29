import pytest

from models.message import WhatsAppMessage
from services.intent import parse_message


def make_msg(body: str) -> WhatsAppMessage:
    return WhatsAppMessage(
        phone="971501234567",
        customer_name="Test User",
        body=body,
        received_at="1716800000",
    )


@pytest.mark.asyncio
async def test_booking_intent_with_code_and_date():
    msg = await parse_message(make_msg("book ITH-A1B2-C3D4 for Friday"))
    assert msg.intent == "booking"
    assert msg.voucher_code == "ITH-A1B2-C3D4"
    assert msg.preferred_date is not None
    assert msg.needs_date_collection is False


@pytest.mark.asyncio
async def test_booking_intent_no_date():
    msg = await parse_message(make_msg("I want to redeem my voucher ITH-A1B2-C3D4"))
    assert msg.intent == "booking"
    assert msg.voucher_code == "ITH-A1B2-C3D4"
    assert msg.needs_date_collection is True


@pytest.mark.asyncio
async def test_support_intent():
    msg = await parse_message(make_msg("I have a problem with my voucher it's expired"))
    assert msg.intent == "support"


@pytest.mark.asyncio
async def test_unknown_intent():
    msg = await parse_message(make_msg("hello"))
    assert msg.intent == "unknown"
