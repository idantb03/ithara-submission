from typing import Optional

from pydantic import BaseModel


class WhatsAppMessage(BaseModel):
    phone: str
    customer_name: str
    body: str
    received_at: str


class ParsedMessage(WhatsAppMessage):
    intent: str
    voucher_code: Optional[str] = None
    preferred_date: Optional[str] = None
    needs_date_collection: bool = False
