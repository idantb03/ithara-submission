import pytest

from services.voucher import validate_voucher


@pytest.mark.asyncio
async def test_valid_voucher():
    result = await validate_voucher("ITH-A1B2-C3D4")
    assert result.valid is True
    assert result.experience == "Relaxing Spa Day for Her"


@pytest.mark.asyncio
async def test_expired_voucher():
    result = await validate_voucher("ITH-X1Y2-Z3W4")
    assert result.valid is False
    assert result.status == "expired"


@pytest.mark.asyncio
async def test_unknown_voucher():
    result = await validate_voucher("ITH-XXXX-XXXX")
    assert result.valid is False
    assert result.status == "not_found"
