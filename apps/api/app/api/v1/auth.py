from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.services.auth_service import AuthService
from app.api.v1.deps import get_current_merchant_user
from app.models.merchant_user import MerchantUser

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session)
):
    """
    POST /api/v1/auth/login
    Authenticates user and issues access token + sets refresh_token cookie.
    """
    auth_service = AuthService(session)
    token_response, user = await auth_service.authenticate_user(payload)
    
    # Set httpOnly cookie for refresh token per §7.1
    if token_response.refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=token_response.refresh_token,
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite="lax",
            max_age=7 * 24 * 3600
        )
    return token_response

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    POST /api/v1/auth/refresh
    Rotates access token using refresh token.
    """
    auth_service = AuthService(session)
    return await auth_service.refresh_access_token(payload.refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: MerchantUser = Depends(get_current_merchant_user)
):
    """
    GET /api/v1/auth/me
    Returns current authenticated merchant user details.
    """
    return UserResponse(
        id=current_user.id,
        merchant_id=current_user.merchant_id,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active
    )
