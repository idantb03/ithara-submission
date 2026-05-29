import httpx

from config import settings
from models.booking import BookingRecord
from models.voucher import VoucherData


async def create_booking(
    voucher: VoucherData,
    customer_phone: str,
    customer_name: str,
    confirmed_date: str,
    confirmed_time: str,
) -> BookingRecord:
    booking = BookingRecord(
        voucher_code=voucher.code or "",
        customer_phone=customer_phone,
        customer_name=customer_name,
        experience_id=voucher.experience_id or "unknown",
        partner_id=voucher.partner_id or "unknown",
        booking_date=confirmed_date,
        booking_time=confirmed_time,
    )
    if settings.DEMO_MODE:
        return booking
    return await _api_create_booking(booking)


async def _api_create_booking(booking: BookingRecord) -> BookingRecord:
    async with httpx.AsyncClient(timeout=6.0) as client:
        response = await client.post(
            f"{settings.ITHARA_API_BASE}/api/bookings",
            headers={"Authorization": f"Bearer {settings.ITHARA_API_KEY}"},
            json=booking.model_dump(),
        )
        response.raise_for_status()
        return BookingRecord(**response.json())
