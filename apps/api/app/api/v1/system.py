from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser
from app.schemas.system import (
    SystemRoadmapResponse,
    SystemResilienceResponse,
    SystemExclusionsResponse
)
from app.services.system_service import SystemService

router = APIRouter(prefix="/system", tags=["System & Governance"])

@router.get("/roadmap", response_model=SystemRoadmapResponse)
async def get_system_roadmap(
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/system/roadmap (§42).
    Retrieve overall system completion roadmap and module completion metrics.
    """
    service = SystemService(session)
    return await service.get_roadmap()

@router.get("/resilience-matrix", response_model=SystemResilienceResponse)
async def get_system_resilience_matrix(
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/system/resilience-matrix (§43).
    Retrieve real-world component resilience metrics, fallback states, and health statuses.
    """
    service = SystemService(session)
    return await service.get_resilience_matrix()

@router.get("/exclusions", response_model=SystemExclusionsResponse)
async def get_system_exclusions(
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/system/exclusions (§44).
    Retrieve explicit v3 exclusions and enterprise safety governance boundaries.
    """
    service = SystemService(session)
    return await service.get_exclusions()
