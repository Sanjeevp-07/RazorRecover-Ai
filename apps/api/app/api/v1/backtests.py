import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser
from app.schemas.backtest import BacktestCreateRequest, BacktestResultResponse
from app.services.backtest_service import BacktestService

router = APIRouter(prefix="/backtests", tags=["Backtests"])

@router.post("", response_model=BacktestResultResponse, status_code=status.HTTP_201_CREATED)
async def create_backtest_simulation(
    req: BacktestCreateRequest,
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    POST /api/v1/backtests (§34 & §40).
    Replay historical dataset in shadow mode through Taxonomy & Baseline Scorer.
    """
    service = BacktestService(session, current_user.merchant_id)
    return await service.run_backtest_simulation(
        historical_records=req.dataset,
        parameters=req.parameters,
        dataset_size=req.dataset_size or 1000
    )

@router.get("/latest", response_model=BacktestResultResponse)
async def get_latest_backtest_result(
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/backtests/latest
    Retrieve the most recent backtest simulation run results for this merchant.
    """
    service = BacktestService(session, current_user.merchant_id)
    run = await service.get_latest_backtest()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No backtest runs found")
    return run

@router.get("/{backtest_id}", response_model=BacktestResultResponse)
async def get_backtest_result(
    backtest_id: uuid.UUID,
    current_user: MerchantUser = Depends(get_current_merchant_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    GET /api/v1/backtests/{id} (§34 & §40).
    Retrieve backtest simulation run results and projected ROI.
    """
    service = BacktestService(session, current_user.merchant_id)
    run = await service.get_backtest_by_id(backtest_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backtest run not found")
    return run
