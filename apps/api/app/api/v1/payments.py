import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser
from app.models.payment import PaymentStatus
from app.schemas.payment import PaymentResponse
from app.schemas.common import PaginatedResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("", response_model=PaginatedResponse[PaymentResponse])
async def list_payments(
    status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/payments (§9.2).
    List/filter payments (paginated), scoped by merchant_id via PaymentService.
    """
    service = PaymentService(session, current_user.merchant_id)
    items, total = await service.list_payments(status_filter=status, page=page, page_size=page_size)

    return PaginatedResponse[PaymentResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get("/{id}", response_model=PaymentResponse)
async def get_payment_detail(
    id: uuid.UUID,
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/payments/{id} (§9.2).
    Payment details, scoped by merchant_id via PaymentService.
    """
    service = PaymentService(session, current_user.merchant_id)
    return await service.get_payment(id)
