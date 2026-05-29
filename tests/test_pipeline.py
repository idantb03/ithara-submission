from unittest.mock import AsyncMock, patch

import pytest

from models.message import WhatsAppMessage
from pipeline import run


def make_msg(body: str) -> WhatsAppMessage:
    return WhatsAppMessage(
        phone="971501234567",
        customer_name="Test User",
        body=body,
        received_at="1716800000",
    )


@pytest.mark.asyncio
async def test_pipeline_unknown_intent_prompts_booking_details():
    with patch("pipeline.send_whatsapp", new=AsyncMock()) as send_whatsapp:
        await run(make_msg("hello there"))
        send_whatsapp.assert_awaited_once()
        assert "voucher code" in send_whatsapp.await_args.args[1]


@pytest.mark.asyncio
async def test_pipeline_support_routes_to_ops():
    with (
        patch("pipeline.send_whatsapp", new=AsyncMock()) as send_whatsapp,
        patch("pipeline.send_email", new=AsyncMock()) as send_email,
    ):
        await run(make_msg("I have a problem with my voucher"))
        send_email.assert_awaited_once()
        send_whatsapp.assert_awaited_once()


@pytest.mark.asyncio
async def test_pipeline_booking_happy_path_sends_customer_and_partner_notifications():
    with (
        patch("pipeline.send_whatsapp", new=AsyncMock()) as send_whatsapp,
        patch("pipeline.send_email", new=AsyncMock()) as send_email,
    ):
        await run(make_msg("book ITH-A1B2-C3D4 for Friday"))
        assert send_whatsapp.await_count == 1
        assert send_email.await_count == 1
