from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser
from app.schemas.analytics import AnalyticsPerformanceResponse
from app.services.recovery_case_service import RecoveryCaseService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/performance", response_model=AnalyticsPerformanceResponse)
async def get_analytics_performance(
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/analytics/performance (§19 & §20.4).
    Returns real-time analytics synchronized with live dashboard metrics.
    """
    service = RecoveryCaseService(session, current_user.merchant_id)
    return await service.get_analytics_performance()
