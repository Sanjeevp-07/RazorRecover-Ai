from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.recovery_case_service import RecoveryCaseService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/dashboard/summary (§9.2).
    Returns failed, recoverable, and recovered revenue KPIs, recovery rate, pending cases, escalations.
    """
    service = RecoveryCaseService(session, current_user.merchant_id)
    return await service.get_dashboard_summary()
