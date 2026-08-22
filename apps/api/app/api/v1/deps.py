import uuid
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.security import decode_token
from app.services.auth_service import AuthService
from app.models.merchant_user import MerchantUser

security = HTTPBearer()

async def get_current_merchant_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session)
) -> MerchantUser:
    """
    Mandatory authentication dependency for protected routes (§7.1).
    Validates JWT Bearer access token and returns authenticated merchant user.
    Uses AuthService (service layer) per architectural layering rules.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        user_id_str = payload.get("sub")
        merchant_id_str = payload.get("merchant_id")
        if not user_id_str or not merchant_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing required claims"
            )
        user_id = uuid.UUID(user_id_str)
        merchant_id = uuid.UUID(merchant_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    auth_service = AuthService(session)
    user = await auth_service.get_user_by_id(user_id)
    if not user or not user.is_active or str(user.merchant_id) != str(merchant_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User or merchant is inactive"
        )

    return user
