from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    POST /api/v1/auth/register
    Register a new merchant account and owner user. Returns access + refresh tokens.
    """
    service = AuthService(session)
    token_response, _ = await service.register_merchant_user(payload)
    return token_response

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    POST /api/v1/auth/login (§7.1)
    Authenticate merchant user email and password. Returns access + refresh tokens.
    Rejects extra unallowed fields via Pydantic extra="forbid" schema rule.
    """
    service = AuthService(session)
    token_response, _ = await service.authenticate_user(payload)
    return token_response

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    POST /api/v1/auth/refresh (§7.1)
    Issue new access token using a valid refresh token.
    """
    service = AuthService(session)
    return await service.refresh_access_token(payload.refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: MerchantUser = Depends(get_current_merchant_user)
):
    """
    GET /api/v1/auth/me (§7.1)
    Retrieve authenticated user profile and merchant scoping information.
    Protected route requiring valid Bearer access token.
    """
    return UserResponse(
        id=current_user.id,
        merchant_id=current_user.merchant_id,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active
    )
