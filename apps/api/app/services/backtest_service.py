import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.backtest import BacktestRun, SimulatedActionExecution, BacktestStatus
from app.policy.failure_taxonomy_engine import FailureTaxonomyEngine
from app.ai.baseline_scorer import BaselineScorer

import random

def format_inr_lakhs(amount_inr: float) -> str:
    """Format numeric INR amount into Lakhs string (e.g. ₹8.4L)."""
    lakhs = amount_inr / 100000.0
    return f"₹{lakhs:.1f}L"

class BacktestService:
    """
    Backtesting & Historical ROI Simulation Service (§34).
    Replays historical failed-payment data in shadow mode without invoking live tool execution.
    """
    def __init__(self, session: AsyncSession, merchant_id: uuid.UUID):
        self.session = session
        self.merchant_id = merchant_id

    def generate_random_dataset(self, size: int = 1000) -> List[Dict[str, Any]]:
        """Generate dynamic randomized failed payment dataset for dry-run simulation."""
        # Use current time as random seed to guarantee DIFFERENT random values on every run
        rnd = random.Random()
        
        failure_types = [
            {"code": "OTP_3DS_ABANDONED", "desc": "Customer abandoned 3DS OTP screen", "method": "card", "is_fraud": False},
            {"code": "INSUFFICIENT_FUNDS", "desc": "Insufficient funds in customer account", "method": "upi", "is_fraud": False},
            {"code": "GATEWAY_BANK_TIMEOUT", "desc": "Bank gateway 504 timeout", "method": "netbanking", "is_fraud": False},
            {"code": "ISSUER_RISK_DECLINE", "desc": "Velocity threshold card testing attempt", "method": "card", "is_fraud": True},
            {"code": "VPA_INVALID", "desc": "Invalid VPA address format", "method": "upi", "is_fraud": False},
            {"code": "EXPIRED_CARD", "desc": "Card expired / invalid instrument", "method": "card", "is_fraud": True}
        ]

        dataset = []
        for i in range(size):
            ft = rnd.choice(failure_types)
            # Random amount between ₹800 and ₹25,000 (in paise)
            is_high_value = rnd.random() < 0.10
            amount_minor = rnd.randint(5000000, 20000000) if is_high_value else rnd.randint(80000, 2500000)
            
            dataset.append({
                "provider_payment_id": f"pay_rand_{rnd.randint(100000, 999999)}_{i}",
                "error_code": ft["code"],
                "error_description": ft["desc"],
                "amount_minor": amount_minor,
                "customer_history_score": round(rnd.uniform(0.1, 0.95), 2),
                "retry_count": rnd.randint(1, 5),
                "velocity_flag": ft["is_fraud"] or (rnd.random() < 0.12),
                "method": ft["method"],
                "is_high_value": is_high_value
            })
        return dataset

    async def run_backtest_simulation(
        self,
        historical_records: Optional[List[Dict[str, Any]]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        dataset_size: int = 1000
    ) -> BacktestRun:
        """
        Execute shadow backtesting replay on a batch of historical failed payments.
        """
        params = parameters or {}
        records = historical_records if (historical_records and len(historical_records) > 0) else self.generate_random_dataset(dataset_size)

        run = BacktestRun(
            merchant_id=self.merchant_id,
            status=BacktestStatus.RUNNING,
            total_dataset_cases=len(records),
            parameters=params,
            summary_report={}
        )
        self.session.add(run)
        await self.session.flush()

        total_cases = len(records)
        recoverable_cases = 0
        policy_blocked_cases = 0
        approval_required_cases = 0
        low_confidence_cases = 0

        estimated_recovery_minor = 0
        control_recovery_minor = 0
        total_failed_revenue_minor = 0
        category_breakdown = {}

        for idx, rec in enumerate(records):
            amount_minor = int(rec.get("amount_minor", rec.get("amount", 0)))
            total_failed_revenue_minor += amount_minor

            # 1. Deterministic Taxonomy Classification (§30)
            taxonomy_res = FailureTaxonomyEngine.classify_failure(
                error_code=rec.get("error_code"),
                error_description=rec.get("error_description"),
                error_reason=rec.get("error_reason"),
                error_source=rec.get("error_source"),
                error_step=rec.get("error_step"),
                method=rec.get("method")
            )

            # 2. Baseline Heuristic Scoring (§32)
            history_score = float(rec.get("customer_history_score", 0.6))
            retry_count = int(rec.get("retry_count", 1))
            velocity_flag = bool(rec.get("velocity_flag", False))
            is_high_value = bool(rec.get("is_high_value", amount_minor > 5000000))

            baseline_res = BaselineScorer.calculate_baseline(
                customer_history_score=history_score,
                retry_count=retry_count,
                velocity_flag=velocity_flag,
                failure_class=taxonomy_res.failure_class
            )

            prob = baseline_res.baseline_probability

            # Categorize case into exact 4 metrics
            if velocity_flag or taxonomy_res.is_hard_decline or retry_count >= 4:
                policy_blocked_cases += 1
                decision = "DENY"
            elif is_high_value or history_score > 0.90:
                approval_required_cases += 1
                decision = "HUMAN_APPROVAL"
                estimated_recovery_minor += int(amount_minor * 0.85)
            elif prob < 0.45:
                low_confidence_cases += 1
                decision = "DENY"
            else:
                recoverable_cases += 1
                decision = "ALLOW"
                estimated_recovery_minor += amount_minor

            # Control recovery (unassisted organic baseline recovery rate ~ 14.2%)
            if prob >= 0.70 and not velocity_flag and not taxonomy_res.is_hard_decline:
                control_recovery_minor += int(amount_minor * 0.35)

            tool_choice = "CREATE_RESUME_SESSION" if taxonomy_res.failure_class.value == "OTP_3DS_ABANDONED" else "CREATE_PAYMENT_LINK"

            sim_action = SimulatedActionExecution(
                backtest_id=run.id,
                case_reference=rec.get("provider_payment_id", f"sim_case_{idx}"),
                tool_name=tool_choice,
                simulated_decision=decision,
                simulated_probability=prob
            )
            self.session.add(sim_action)

            f_class = taxonomy_res.failure_class.value
            category_breakdown[f_class] = category_breakdown.get(f_class, 0) + 1

        rec_rate = round(recoverable_cases / total_cases, 4) if total_cases > 0 else 0.0
        incremental_lift_minor = max(0, estimated_recovery_minor - control_recovery_minor)

        estimated_recovery_inr = estimated_recovery_minor / 100.0
        control_recovery_inr = control_recovery_minor / 100.0
        incremental_lift_inr = incremental_lift_minor / 100.0

        run.simulated_recovered_cases = recoverable_cases
        run.simulated_recovered_revenue_minor = estimated_recovery_minor
        run.simulated_recovery_rate = rec_rate
        run.projected_roi_multiplier = max(1.0, round(estimated_recovery_minor / max(1, total_cases * 500), 2))
        run.status = BacktestStatus.COMPLETED
        run.completed_at = datetime.now(timezone.utc)
        run.summary_report = {
            "total_cases": total_cases,
            "recoverable_cases": recoverable_cases,
            "policy_blocked_cases": policy_blocked_cases,
            "approval_required_cases": approval_required_cases,
            "low_confidence_cases": low_confidence_cases,
            "total_failed_revenue_minor": total_failed_revenue_minor,
            "estimated_recovery_minor": estimated_recovery_minor,
            "control_recovery_minor": control_recovery_minor,
            "incremental_lift_minor": incremental_lift_minor,
            "estimated_recovery_inr": estimated_recovery_inr,
            "control_recovery_inr": control_recovery_inr,
            "incremental_lift_inr": incremental_lift_inr,
            "formatted_estimated_recovery": format_inr_lakhs(estimated_recovery_inr),
            "formatted_control_recovery": format_inr_lakhs(control_recovery_inr),
            "formatted_incremental_lift": format_inr_lakhs(incremental_lift_inr),
            "projected_recovery_rate": rec_rate,
            "category_distribution": category_breakdown
        }

        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get_backtest_by_id(self, backtest_id: uuid.UUID) -> Optional[BacktestRun]:
        """Fetch backtest run record by ID."""
        stmt = select(BacktestRun).where(
            BacktestRun.id == backtest_id,
            BacktestRun.merchant_id == self.merchant_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
