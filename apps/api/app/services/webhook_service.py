import uuid
import json
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.integrations.razorpay.webhook import verify_razorpay_signature
from app.core.crypto import decrypt_secret
from app.repositories.merchant_repository import MerchantRepository
from app.repositories.webhook_repository import WebhookRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.case_repository import CaseRepository
from app.models.webhook_event import WebhookEvent, WebhookProcessingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.recovery_case import RecoveryCase, RecoveryCaseStatus
from app.services.state_machine import StateMachineManager

class WebhookService:
    """Service layer handling Razorpay Webhook Ingestion & Event Processing (§10.2)."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def ingest_razorpay_webhook(
        self,
        raw_body: bytes,
        signature: str,
        external_event_id: str,
        merchant_id: uuid.UUID
    ) -> Tuple[WebhookEvent, bool]:
        """
        Ingest, verify signature, and deduplicate incoming Razorpay webhook event (§10.2).
        Returns (webhook_event, is_duplicate).
        """
        # Fetch merchant details to get decrypted webhook secret
        merchant_repo = MerchantRepository(self.session)
        merchant = await merchant_repo.get_by_id(merchant_id)
        if not merchant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

        decrypted_secret = decrypt_secret(merchant.razorpay_webhook_secret_enc)
        
        # Verify HMAC-SHA256 signature
        if not verify_razorpay_signature(raw_body, signature, decrypted_secret):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Razorpay webhook signature"
            )

        # Parse JSON payload post-verification
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed JSON payload")

        webhook_repo = WebhookRepository(self.session, merchant_id)
        
        # Deduplication check via external_event_id (§10.2)
        existing_event = await webhook_repo.get_by_external_id(external_event_id)
        if existing_event:
            # Duplicate event -> no-op, return 200
            return existing_event, True

        event_type = payload.get("event", "unknown")
        
        # Persist event
        event = WebhookEvent(
            merchant_id=merchant_id,
            external_event_id=external_event_id,
            event_type=event_type,
            raw_payload=payload,
            processing_status=WebhookProcessingStatus.RECEIVED
        )
        event = await webhook_repo.add(event)
        
        # Process domain state updates (§10.1)
        await self.process_webhook_domain_event(merchant_id, event_type, payload)
        
        await self.session.commit()
        return event, False

    async def process_webhook_domain_event(self, merchant_id: uuid.UUID, event_type: str, payload: dict):
        """Map webhook event to domain state updates (§10.1)."""
        payment_repo = PaymentRepository(self.session, merchant_id)
        case_repo = CaseRepository(self.session, merchant_id)
        state_mgr = StateMachineManager(self.session)

        contains_entity = payload.get("payload", {})

        if event_type == "payment.failed":
            payment_entity = contains_entity.get("payment", {}).get("entity", {})
            provider_payment_id = payment_entity.get("id")
            if provider_payment_id:
                payment = await payment_repo.get_by_provider_id(provider_payment_id)
                if not payment:
                    payment = Payment(
                        merchant_id=merchant_id,
                        provider_payment_id=provider_payment_id,
                        amount_minor=payment_entity.get("amount", 0),
                        currency=payment_entity.get("currency", "INR"),
                        status=PaymentStatus.FAILED,
                        failure_reason=payment_entity.get("error_reason") or payment_entity.get("error_description"),
                        method=payment_entity.get("method")
                    )
                    payment = await payment_repo.add(payment)

                # Create a recovery_case if none open for this payment (§10.1)
                open_case = await case_repo.get_open_case_by_payment_id(payment.id)
                if not open_case:
                    correlation_id = uuid.uuid4()
                    new_case = RecoveryCase(
                        merchant_id=merchant_id,
                        payment_id=payment.id,
                        status=RecoveryCaseStatus.OPEN,
                        correlation_id=correlation_id
                    )
                    new_case = await case_repo.add(new_case)
                    await case_repo.add_audit_log(
                        correlation_id=correlation_id,
                        event_type="CASE_CREATED",
                        payload={"case_id": str(new_case.id), "payment_id": str(payment.id)}
                    )

        elif event_type == "payment.captured":
            payment_entity = contains_entity.get("payment", {}).get("entity", {})
            provider_payment_id = payment_entity.get("id")
            if provider_payment_id:
                payment = await payment_repo.get_by_provider_id(provider_payment_id)
                if payment:
                    payment.status = PaymentStatus.CAPTURED
                    open_case = await case_repo.get_open_case_by_payment_id(payment.id)
                    if open_case:
                        open_case.status = RecoveryCaseStatus.RECOVERED
                        await case_repo.add_audit_log(
                            correlation_id=open_case.correlation_id,
                            event_type="CASE_RECOVERED",
                            payload={"reason": "payment.captured_webhook"}
                        )
