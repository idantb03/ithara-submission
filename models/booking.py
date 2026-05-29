from typing import Optional

from pydantic import BaseModel, Field


class AvailabilityResult(BaseModel):
    available: bool
    confirmed_date: Optional[str] = None
    confirmed_time: Optional[str] = None
    notes: Optional[str] = None
    alternative_slots: list[str] = Field(default_factory=list)
    fail_reason: Optional[str] = None


class BookingRecord(BaseModel):
    voucher_code: str
    customer_phone: str
    customer_name: str
    experience_id: str
    partner_id: str
    booking_date: str
    booking_time: str
    status: str = "confirmed"
    created_via: str = "whatsapp_automation"
