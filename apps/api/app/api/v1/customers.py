import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser
from app.schemas.preferences import CommunicationPreferenceUpdate, CommunicationPreferenceResponse
from app.services.compliance_service import ComplianceService

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/{customer_id}/communication-preferences", response_model=List[CommunicationPreferenceResponse])
async def get_customer_communication_preferences(
    customer_id: uuid.UUID,
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/customers/{id}/communication-preferences (§35 & §40).
    Retrieve DPDP per-channel communication consent preferences.
    """
    service = ComplianceService(session)
    return await service.get_customer_preferences(customer_id)

@router.put("/{customer_id}/communication-preferences", response_model=CommunicationPreferenceResponse)
async def update_customer_communication_preference(
    customer_id: uuid.UUID,
    req: CommunicationPreferenceUpdate,
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    PUT /api/v1/customers/{id}/communication-preferences (§35 & §40).
    Record or update customer opt-in/opt-out consent.
    """
    service = ComplianceService(session)
    return await service.update_customer_preference(
        customer_id=customer_id,
        channel=req.channel,
        opt_in=req.opt_in,
        purpose=req.purpose or "payment_recovery_outreach"
    )
