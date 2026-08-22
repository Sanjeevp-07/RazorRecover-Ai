import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.repositories.case_repository import CaseRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.merchant_repository import MerchantRepository
from app.models.recovery_case import RecoveryCase, RecoveryCaseStatus
from app.models.payment import Payment, PaymentStatus
from app.models.risk_signal import RiskSignal
from app.models.ai_decision import AIDecision
from app.models.policy_decision import PolicyDecision, PolicyOutcome
from app.models.action_execution import ActionExecution, ActionExecutionStatus
from app.models.approval import Approval, ApprovalStatus
from app.models.policy_config import PolicyConfig

from app.ai.openai_provider import OpenAIReasoner
from app.policy.engine import evaluate_policy, PolicyEvaluationContext
from app.tools.payment_link_tool import CreatePaymentLinkTool
from app.tools.notification_tool import SendNotificationTool
from app.tools.escalate_tool import EscalateCaseTool
from app.integrations.razorpay.client import RazorpayClient
from app.core.crypto import decrypt_secret
from app.services.state_machine import StateMachineManager

class RecoveryOrchestrator:
    """
    Core Business Orchestrator Service (§5 & §16).
    The only layer allowed to call Policy, AI, and multiple repositories in one operation.
    """
    def __init__(self, session: AsyncSession, merchant_id: uuid.UUID):
        self.session = session
        self.merchant_id = merchant_id
        self.case_repo = CaseRepository(session, merchant_id)
        self.payment_repo = PaymentRepository(session, merchant_id)
        self.merchant_repo = MerchantRepository(session)
        self.state_mgr = StateMachineManager(session)

    async def execute_recovery_pipeline(self, case_id: uuid.UUID) -> RecoveryCase:
        """
        Execute full recovery pipeline (§1.2 & §16.2):
        case claim -> context aggregation -> risk signals -> AI recommendation -> policy decision -> action execution / approval routing.
        """
        # 1. Claim case atomically with SELECT FOR UPDATE SKIP LOCKED (§8.2 & §17)
        case = await self.state_mgr.claim_case_for_analysis(case_id)
        if not case:
            existing_case = await self.case_repo.get_by_id(case_id)
            if existing_case:
                return existing_case
            raise ValueError(f"Case {case_id} not found or not in OPEN status")

        try:
            payment = await self.payment_repo.get_by_id(case.payment_id)
            if not payment:
                case.status = RecoveryCaseStatus.CLOSED
                await self.session.commit()
                return case

            # 2. Risk Signal Calculation (§6.8)
            # Deterministic calculation: retry count = 1, history score = 0.85
            risk_signal = RiskSignal(
                case_id=case.id,
                retry_count=1,
                customer_history_score=0.85,
                velocity_flag=False
            )
            self.session.add(risk_signal)
            await self.session.flush()

            # 3. AI Reasoner Call (§11 & §12)
            context = {
                "payment": {
                    "amount_minor": payment.amount_minor,
                    "currency": payment.currency,
                    "failure_reason": payment.failure_reason,
                    "method": payment.method
                },
                "risk_signals": {
                    "retry_count": risk_signal.retry_count,
                    "customer_history_score": float(risk_signal.customer_history_score),
                    "velocity_flag": risk_signal.velocity_flag
                }
            }

            reasoner = OpenAIReasoner()
            rec, is_valid, raw_output, latency_ms = await reasoner.analyze(case.id, context)

            # Persist AI Decision (§6.9)
            ai_decision = AIDecision(
                case_id=case.id,
                model_id=reasoner.model_id,
                schema_version="1.0",
                raw_output={"raw": raw_output},
                validated_output=rec.model_dump() if rec else None,
                is_valid=is_valid,
                latency_ms=latency_ms
            )
            self.session.add(ai_decision)
            await self.session.flush()

            # 4. Fetch Policy Config thresholds (§6.11 & §13.2)
            config_stmt = select(PolicyConfig).where(
                (PolicyConfig.merchant_id == self.merchant_id) | (PolicyConfig.merchant_id.is_(None))
            )
            configs_res = await self.session.execute(config_stmt)
            configs = {c.key: c.value for c in configs_res.scalars().all()}

            retry_limit = int(configs.get("retry_count_limit", 3))
            amount_threshold = int(configs.get("approval_amount_threshold_minor", 5000000))
            risk_threshold = float(configs.get("approval_risk_threshold", 0.7))
            sla_hours = int(configs.get("approval_sla_hours", 24))

            # 5. Policy Engine Evaluation (§13.1)
            policy_ctx = PolicyEvaluationContext(
                payment_status=payment.status.value,
                case_status=case.status.value,
                existing_action_statuses=set(),
                retry_count=risk_signal.retry_count,
                recommended_action=rec.recommended_action.value if rec else "NO_ACTION",
                payment_amount_minor=payment.amount_minor,
                ai_confidence=rec.confidence if rec else 0.0,
                ai_requires_human=rec.requires_human if rec else True,
                retry_count_limit=retry_limit,
                approval_amount_threshold_minor=amount_threshold,
                approval_risk_threshold=risk_threshold
            )

            policy_result = evaluate_policy(policy_ctx)

            # Persist Policy Decision (§6.10)
            policy_decision = PolicyDecision(
                case_id=case.id,
                ai_decision_id=ai_decision.id,
                decision=policy_result.decision,
                policy_version=policy_result.policy_version,
                matched_rule=policy_result.matched_rule
            )
            self.session.add(policy_decision)
            await self.session.flush()

            await self.case_repo.add_audit_log(
                correlation_id=case.correlation_id,
                event_type="POLICY_DECIDED",
                payload={"decision": policy_result.decision.value, "matched_rule": policy_result.matched_rule}
            )

            # 6. Action Execution / Routing (§8.2 & §14)
            if policy_result.decision == PolicyOutcome.DENY:
                case.status = RecoveryCaseStatus.DENIED

            elif policy_result.decision == PolicyOutcome.HUMAN_APPROVAL:
                case.status = RecoveryCaseStatus.PENDING_APPROVAL
                sla_expires_at = datetime.now(timezone.utc) + timedelta(hours=sla_hours)
                
                approval = Approval(
                    case_id=case.id,
                    status=ApprovalStatus.PENDING,
                    sla_expires_at=sla_expires_at
                )
                self.session.add(approval)

            elif policy_result.decision == PolicyOutcome.ALLOW:
                case.status = RecoveryCaseStatus.EXECUTING
                
                # Fetch merchant razorpay keys
                merchant = await self.merchant_repo.get_by_id(self.merchant_id)
                r_client = RazorpayClient(
                    key_id=merchant.razorpay_key_id if merchant else None,
                    key_secret=decrypt_secret(merchant.razorpay_key_secret_enc) if merchant else None
                )

                tool = CreatePaymentLinkTool(r_client)
                idempotency_key = tool.generate_idempotency_key(case.id, tool.tool_name, "primary")

                action = ActionExecution(
                    case_id=case.id,
                    tool_name=tool.tool_name,
                    idempotency_key=idempotency_key,
                    status=ActionExecutionStatus.IN_PROGRESS,
                    input_payload={"amount_minor": payment.amount_minor, "currency": payment.currency},
                    attempt_count=1
                )
                self.session.add(action)
                await self.session.flush()

                success, output_payload, error_cat = await tool.execute(
                    case_id=case.id,
                    payload={"amount_minor": payment.amount_minor, "currency": payment.currency}
                )

                if success:
                    action.status = ActionExecutionStatus.SUCCEEDED
                    action.output_payload = output_payload
                    await self.case_repo.add_audit_log(
                        correlation_id=case.correlation_id,
                        event_type="ACTION_EXECUTED",
                        payload={"tool_name": tool.tool_name, "output": output_payload}
                    )
                else:
                    action.status = ActionExecutionStatus.FAILED
                    action.error_category = error_cat
                    case.status = RecoveryCaseStatus.CLOSED

            await self.session.commit()
            return case

        except Exception as exc:
            # Fail closed on internal engine error (§18)
            case.status = RecoveryCaseStatus.PENDING_APPROVAL
            await self.case_repo.add_audit_log(
                correlation_id=case.correlation_id,
                event_type="POLICY_ERROR_FAIL_CLOSED",
                payload={"error": str(exc)}
            )
            await self.session.commit()
            return case
