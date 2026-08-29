import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.backtest import BacktestRun, SimulatedActionExecution, BacktestStatus
from app.policy.failure_taxonomy_engine import FailureTaxonomyEngine
from app.ai.baseline_scorer import BaselineScorer

class BacktestService:
    """
    Backtesting & Historical ROI Simulation Service (§34).
    Replays historical failed-payment data in shadow mode without invoking live tool execution.
    """
    def __init__(self, session: AsyncSession, merchant_id: uuid.UUID):
        self.session = session
        self.merchant_id = merchant_id

    async def run_backtest_simulation(
        self,
        historical_records: List[Dict[str, Any]],
        parameters: Optional[Dict[str, Any]] = None
    ) -> BacktestRun:
        """
        Execute shadow backtesting replay on a batch of historical failed payments.
        """
        params = parameters or {}
        run = BacktestRun(
            merchant_id=self.merchant_id,
            status=BacktestStatus.RUNNING,
            total_dataset_cases=len(historical_records),
            parameters=params,
            summary_report={}
        )
        self.session.add(run)
        await self.session.flush()

        total_cases = len(historical_records)
        simulated_recovered_cases = 0
        simulated_recovered_revenue_minor = 0
        total_failed_revenue_minor = 0
        category_breakdown = {}

        for idx, rec in enumerate(historical_records):
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
            baseline_res = BaselineScorer.calculate_baseline(
                customer_history_score=history_score,
                retry_count=retry_count,
                velocity_flag=bool(rec.get("velocity_flag", False)),
                failure_class=taxonomy_res.failure_class
            )

            # Determine simulation outcome
            is_recovered = baseline_res.baseline_probability >= 0.45 and not taxonomy_res.is_hard_decline
            if is_recovered:
                simulated_recovered_cases += 1
                simulated_recovered_revenue_minor += amount_minor

            tool_choice = "CREATE_RESUME_SESSION" if taxonomy_res.failure_class.value == "OTP_3DS_ABANDONED" else "CREATE_PAYMENT_LINK"

            # Create shadow execution (§34)
            sim_action = SimulatedActionExecution(
                backtest_id=run.id,
                case_reference=rec.get("provider_payment_id", f"sim_case_{idx}"),
                tool_name=tool_choice,
                simulated_decision="ALLOW" if is_recovered else "DENY",
                simulated_probability=baseline_res.baseline_probability
            )
            self.session.add(sim_action)

            # Track category breakdown
            f_class = taxonomy_res.failure_class.value
            category_breakdown[f_class] = category_breakdown.get(f_class, 0) + 1

        rec_rate = round(simulated_recovered_cases / total_cases, 4) if total_cases > 0 else 0.0
        roi_multiplier = round((simulated_recovered_revenue_minor / (total_cases * 500)) if total_cases > 0 else 1.0, 2)

        run.simulated_recovered_cases = simulated_recovered_cases
        run.simulated_recovered_revenue_minor = simulated_recovered_revenue_minor
        run.simulated_recovery_rate = rec_rate
        run.projected_roi_multiplier = max(1.0, roi_multiplier)
        run.status = BacktestStatus.COMPLETED
        run.completed_at = datetime.now(timezone.utc)
        run.summary_report = {
            "total_cases": total_cases,
            "total_failed_revenue_minor": total_failed_revenue_minor,
            "simulated_recovered_revenue_minor": simulated_recovered_revenue_minor,
            "projected_recovery_rate": rec_rate,
            "category_distribution": category_breakdown,
            "baseline_lift_estimate": round(rec_rate - 0.142, 4)
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
