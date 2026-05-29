from typing import Optional

from pydantic import BaseModel


class VoucherData(BaseModel):
    valid: bool
    status: str
    code: Optional[str] = None
    experience: Optional[str] = None
    experience_id: Optional[str] = None
    partner_id: Optional[str] = None
    partner_name: Optional[str] = None
    partner_email: Optional[str] = None
    partner_whatsapp: Optional[str] = None
    expires_at: Optional[str] = None
    message: Optional[str] = None
