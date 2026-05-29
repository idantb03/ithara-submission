import httpx

from config import settings
from mock.partners import MOCK_AVAILABILITY
from models.booking import AvailabilityResult
from models.voucher import VoucherData
from services.notifier import send_email


async def check_availability(voucher: VoucherData, preferred_date: str) -> AvailabilityResult:
    if settings.DEMO_MODE:
        return _mock_check(voucher.partner_id or "", preferred_date)
    if await _partner_has_api(voucher.partner_id or ""):
        return await _api_check(voucher, preferred_date)
    return await _email_check(voucher, preferred_date)


def _mock_check(partner_id: str, preferred_date: str) -> AvailabilityResult:
    data = MOCK_AVAILABILITY.get(partner_id, {})
    if data.get("available", False):
        return AvailabilityResult(
            available=True,
            confirmed_date=preferred_date or data.get("next_slot"),
            confirmed_time=data.get("default_time", "10:00 AM"),
            notes=data.get("notes", ""),
        )
    return AvailabilityResult(
        available=False,
        fail_reason="Partner unavailable for requested date",
        alternative_slots=data.get("alternatives", []),
    )


async def _partner_has_api(partner_id: str) -> bool:
    return bool(partner_id and False)


async def _api_check(voucher: VoucherData, preferred_date: str) -> AvailabilityResult:
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            response = await client.post(
                f"{settings.ITHARA_API_BASE}/api/partners/{voucher.partner_id}/availability",
                headers={"Authorization": f"Bearer {settings.ITHARA_API_KEY}"},
                json={"preferred_date": preferred_date, "experience_id": voucher.experience_id},
            )
            response.raise_for_status()
            return AvailabilityResult(**response.json())
        except Exception:
            return await _email_check(voucher, preferred_date)


async def _email_check(voucher: VoucherData, preferred_date: str) -> AvailabilityResult:
    subject = f"Availability Request - {voucher.experience} - {preferred_date}"
    body = (
        f"Hi {voucher.partner_name},\n\n"
        f"A customer would like to book {voucher.experience} on {preferred_date}.\n\n"
        f"Voucher: {voucher.code}\n\n"
        f"Please confirm availability by replying to this email, or call us at [ops number].\n\n"
        f"- Ithara Bookings Team"
    )
    await send_email(
        to=voucher.partner_email or settings.OPS_EMAIL,
        subject=subject,
        body=body,
    )
    return AvailabilityResult(
        available=False,
        fail_reason="Availability request sent to partner. Ops team will confirm.",
    )
