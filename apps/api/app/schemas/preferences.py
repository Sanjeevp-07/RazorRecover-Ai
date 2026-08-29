import uuid
from datetime import datetime
from typing import Optional
from app.schemas.base import BaseSchema

class CommunicationPreferenceUpdate(BaseSchema):
    """Schema for updating DPDP customer communication consent (§35)."""
    channel: str
    opt_in: bool
    purpose: Optional[str] = "payment_recovery_outreach"

class CommunicationPreferenceResponse(BaseSchema):
    """Schema for DPDP customer communication preference record (§35)."""
    id: uuid.UUID
    customer_id: uuid.UUID
    channel: str
    opt_in: bool
    purpose: str
    consent_timestamp: datetime
