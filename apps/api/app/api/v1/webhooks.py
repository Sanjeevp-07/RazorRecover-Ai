import uuid
from fastapi import APIRouter, Request, Header, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(..., alias="X-Razorpay-Signature"),
    x_razorpay_event_id: str = Header(..., alias="x-razorpay-event-id"),
    merchant_id: str = Header(..., alias="X-Merchant-Id"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    POST /api/v1/webhooks/razorpay (§9.2 & §10.2).
    Verifies HMAC-SHA256 signature against raw body, deduplicates event ID,
    persists event, and returns HTTP 200 within request threshold.
    """
    raw_body = await request.body()
    try:
        m_uuid = uuid.UUID(merchant_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-Merchant-Id header format")

    service = WebhookService(session)
    event, is_duplicate = await service.ingest_razorpay_webhook(
        raw_body=raw_body,
        signature=x_razorpay_signature,
        external_event_id=x_razorpay_event_id,
        merchant_id=m_uuid
    )

    return {
        "status": "success",
        "event_id": str(event.id),
        "external_event_id": event.external_event_id,
        "duplicate": is_duplicate
    }
