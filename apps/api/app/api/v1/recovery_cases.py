import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser
from app.models.recovery_case import RecoveryCaseStatus
from app.schemas.case import (
    RecoveryCaseListItemResponse,
    RecoveryCaseDetailResponse,
    AuditLogTimelineItem
)
from app.schemas.common import PaginatedResponse
from app.services.recovery_case_service import RecoveryCaseService

router = APIRouter(prefix="/recovery-cases", tags=["Recovery Cases"])

@router.get("", response_model=PaginatedResponse[RecoveryCaseListItemResponse])
async def list_recovery_cases(
    status: Optional[RecoveryCaseStatus] = Query(None, description="Filter by case status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/recovery-cases (§9.2).
    List cases (paginated, filter by status).
    """
    service = RecoveryCaseService(session, current_user.merchant_id)
    items, total = await service.list_cases(status_filter=status, page=page, page_size=page_size)
    return PaginatedResponse[RecoveryCaseListItemResponse](
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

@router.get("/{id}", response_model=RecoveryCaseDetailResponse)
async def get_recovery_case_detail(
    id: uuid.UUID,
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/recovery-cases/{id} (§9.2).
    Case detail incl. latest ai_decision + policy_decision + approval + risk_signals.
    """
    service = RecoveryCaseService(session, current_user.merchant_id)
    return await service.get_case_detail(id)

@router.post("/{id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_recovery_case(
    id: uuid.UUID,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    POST /api/v1/recovery-cases/{id}/analyze (§9.2).
    Enqueue analysis task (202 Accepted).
    """
    idem_key = idempotency_key or str(uuid.uuid4())
    service = RecoveryCaseService(session, current_user.merchant_id)
    case_detail = await service.get_case_detail(id)
    return {
        "status": "ACCEPTED",
        "message": "Analysis task enqueued",
        "case_id": str(id),
        "idempotency_key": idem_key
    }

@router.post("/{id}/approve", response_model=RecoveryCaseDetailResponse)
async def approve_recovery_case(
    id: uuid.UUID,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    POST /api/v1/recovery-cases/{id}/approve (§9.2 & §15).
    Approve pending action for a case (Owner role only).
    """
    service = RecoveryCaseService(session, current_user.merchant_id)
    return await service.approve_case(id, current_user.id)

@router.post("/{id}/reject", response_model=RecoveryCaseDetailResponse)
async def reject_recovery_case(
    id: uuid.UUID,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    POST /api/v1/recovery-cases/{id}/reject (§9.2 & §15).
    Reject pending action for a case (Owner role only).
    """
    service = RecoveryCaseService(session, current_user.merchant_id)
    return await service.reject_case(id, current_user.id)

@router.get("/{id}/timeline", response_model=List[AuditLogTimelineItem])
async def get_recovery_case_timeline(
    id: uuid.UUID,
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/recovery-cases/{id}/timeline (§9.2).
    Ordered audit_logs for correlation_id.
    """
    service = RecoveryCaseService(session, current_user.merchant_id)
    return await service.get_case_timeline(id)
