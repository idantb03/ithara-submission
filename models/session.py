from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field


def _default_expiry() -> datetime:
    return datetime.now() + timedelta(hours=24)


class BookingSession(BaseModel):
    session_id: str
    phone: str
    step: str
    voucher_code: Optional[str] = None
    voucher_data: Optional[dict] = None
    preferred_date: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(default_factory=_default_expiry)
