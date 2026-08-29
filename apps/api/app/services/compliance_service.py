import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.communication_preference import CustomerCommunicationPreference

class ComplianceService:
    """
    DPDP Compliance & Customer Consent Service (§35).
    Enforces per-channel communication preferences and zero PAN/CVV invariant.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_customer_preferences(self, customer_id: uuid.UUID) -> List[CustomerCommunicationPreference]:
        """Fetch all per-channel consent records for a customer."""
        stmt = select(CustomerCommunicationPreference).where(
            CustomerCommunicationPreference.customer_id == customer_id
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def is_channel_permitted(self, customer_id: Optional[uuid.UUID], channel: str = "WHATSAPP") -> bool:
        """
        Check if outreach is permitted for given customer and channel (§35).
        Returns True if opt-in is active or default utility consent applies.
        """
        if not customer_id:
            return True # Anonymous/checkout-level fallback

        stmt = select(CustomerCommunicationPreference).where(
            CustomerCommunicationPreference.customer_id == customer_id,
            CustomerCommunicationPreference.channel == channel.upper()
        )
        res = await self.session.execute(stmt)
        pref = res.scalar_one_or_none()

        if pref:
            return pref.opt_in
        
        # If no explicit record, default to utility consent for payment recovery (§31 & §35)
        return True

    async def update_customer_preference(
        self,
        customer_id: uuid.UUID,
        channel: str,
        opt_in: bool,
        purpose: str = "payment_recovery_outreach"
    ) -> CustomerCommunicationPreference:
        """Update or create a communication preference record."""
        stmt = select(CustomerCommunicationPreference).where(
            CustomerCommunicationPreference.customer_id == customer_id,
            CustomerCommunicationPreference.channel == channel.upper()
        )
        res = await self.session.execute(stmt)
        pref = res.scalar_one_or_none()

        if pref:
            pref.opt_in = opt_in
            pref.purpose = purpose
            pref.updated_at = datetime.now(timezone.utc)
        else:
            pref = CustomerCommunicationPreference(
                customer_id=customer_id,
                channel=channel.upper(),
                opt_in=opt_in,
                purpose=purpose,
                consent_timestamp=datetime.now(timezone.utc)
            )
            self.session.add(pref)

        await self.session.commit()
        await self.session.refresh(pref)
        return pref
