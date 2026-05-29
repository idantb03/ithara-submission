import httpx

from config import settings
from mock.vouchers import MOCK_VOUCHERS
from models.voucher import VoucherData


async def validate_voucher(code: str) -> VoucherData:
    if settings.DEMO_MODE:
        return _mock_validate(code)
    return await _api_validate(code)


def _mock_validate(code: str) -> VoucherData:
    data = MOCK_VOUCHERS.get(code.upper())
    if data:
        return VoucherData(**data)
    return VoucherData(
        valid=False,
        status="not_found",
        message="Voucher code not found. Please double-check and try again.",
    )


async def _api_validate(code: str) -> VoucherData:
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(
                f"{settings.ITHARA_API_BASE}/api/vouchers/{code}",
                headers={"Authorization": f"Bearer {settings.ITHARA_API_KEY}"},
            )
            response.raise_for_status()
            return VoucherData(**response.json())
        except httpx.TimeoutException:
            return VoucherData(
                valid=False,
                status="error",
                message="Could not verify your voucher right now. Our team will check and follow up.",
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return VoucherData(valid=False, status="not_found", message="Voucher code not found.")
            return VoucherData(
                valid=False,
                status="error",
                message="Something went wrong. Our team has been notified.",
            )
