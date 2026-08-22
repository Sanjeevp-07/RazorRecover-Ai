import uuid
from datetime import datetime
from typing import Optional
from app.schemas.base import BaseSchema
from app.models.payment import PaymentStatus

class PaymentResponse(BaseSchema):
    """Payment record response schema."""
    id: uuid.UUID
    merchant_id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    customer_id: Optional[uuid.UUID] = None
    provider_payment_id: str
    amount_minor: int
    currency: str
    status: PaymentStatus
    failure_reason: Optional[str] = None
    method: Optional[str] = None
    created_at: datetime
    updated_at: datetime
