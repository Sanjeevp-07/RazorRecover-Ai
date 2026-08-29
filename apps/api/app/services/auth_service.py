import uuid
import httpx
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.repositories.merchant_repository import MerchantRepository
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.models.merchant_user import MerchantUser, UserRole
from app.models.merchant import Merchant
from app.core.crypto import encrypt_secret

DEMO_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

class AuthService:
    """Service layer handling merchant user authentication via Supabase Auth & local storage."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.merchant_repo = MerchantRepository(session)

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[MerchantUser]:
        """Retrieve user by ID via repository with fallback."""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if user:
                return user
        except Exception:
            pass

        # Fallback for demo merchant owner
        if str(user_id) == str(DEMO_USER_ID):
            return MerchantUser(
                id=DEMO_USER_ID,
                merchant_id=DEMO_MERCHANT_ID,
                email="owner@merchant.com",
                password_hash="mock",
                role=UserRole.OWNER,
                is_active=True
            )
        return None

    async def _authenticate_with_supabase(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Attempt authentication using Supabase Auth REST API."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            return None

        url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/token?grant_type=password"
        headers = {
          "apikey": settings.SUPABASE_ANON_KEY,
          "Content-Type": "application/json"
        }
        payload = {"email": email, "password": password}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    return res.json()
        except Exception:
            pass
        return None

    async def authenticate_user(self, payload: LoginRequest) -> Tuple[TokenResponse, MerchantUser]:
        """Authenticate user credentials against Supabase Auth & DB repository."""
        clean_email = payload.email.strip().lower()
        supabase_auth_result = await self._authenticate_with_supabase(clean_email, payload.password)
        
        user = None
        try:
            user = await self.user_repo.get_by_email(clean_email)
        except Exception:
            user = None

        if supabase_auth_result and not user:
            # User authenticated via Supabase; provision local DB merchant & user profile
            sp_user = supabase_auth_result.get("user", {})
            user_id = uuid.UUID(sp_user.get("id")) if sp_user.get("id") else uuid.uuid4()
            merchant_name = sp_user.get("user_metadata", {}).get("merchant_name", f"{clean_email.split('@')[0]} Enterprise")
            
            user = await self.provision_merchant_and_user(
                user_id=user_id,
                email=clean_email,
                password=payload.password,
                merchant_name=merchant_name
            )

        # Fallback seeding for demo credentials
        if not user and clean_email == "owner@merchant.com" and payload.password == "password123":
            try:
                user = await self.create_demo_merchant_owner_if_not_exists(
                    email=clean_email,
                    password=payload.password,
                    merchant_name="Demo Merchant Enterprise"
                )
            except Exception:
                user = MerchantUser(
                    id=DEMO_USER_ID,
                    merchant_id=DEMO_MERCHANT_ID,
                    email="owner@merchant.com",
                    password_hash=get_password_hash("password123"),
                    role=UserRole.OWNER,
                    is_active=True
                )

        if not user or (not supabase_auth_result and not verify_password(payload.password, user.password_hash)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Merchant account is inactive"
            )

        try:
            user.last_login_at = datetime.now(timezone.utc)
            await self.session.commit()
        except Exception:
            pass

        access_token = supabase_auth_result.get("access_token") if supabase_auth_result else create_access_token(
            subject=str(user.id),
            merchant_id=str(user.merchant_id)
        )
        refresh_token = supabase_auth_result.get("refresh_token") if supabase_auth_result else create_refresh_token(
            subject=str(user.id),
            merchant_id=str(user.merchant_id)
        )

        user_info = UserResponse(
            id=user.id,
            merchant_id=user.merchant_id,
            email=user.email,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            is_active=user.is_active
        )

        token_response = TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token,
            user=user_info
        )
        return token_response, user

    async def provision_merchant_and_user(
        self,
        user_id: uuid.UUID,
        email: str,
        password: str,
        merchant_name: str
    ) -> MerchantUser:
        """Provision a new merchant and owner user in the database."""
        clean_email = email.strip().lower()

        # Check if user already exists
        existing = await self.user_repo.get_by_email(clean_email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        merchant_id = uuid.uuid4()
        merchant = Merchant(
            id=merchant_id,
            name=merchant_name,
            razorpay_key_id=settings.RAZORPAY_KEY_ID,
            razorpay_key_secret_enc=encrypt_secret(settings.RAZORPAY_KEY_SECRET),
            razorpay_webhook_secret_enc=encrypt_secret(settings.RAZORPAY_WEBHOOK_SECRET)
        )
        try:
            merchant = await self.merchant_repo.add(merchant)
        except Exception:
            await self.session.rollback()
            merchant = None

        user = MerchantUser(
            id=user_id,
            merchant_id=merchant.id if merchant else merchant_id,
            email=clean_email,
            password_hash=get_password_hash(password),
            role=UserRole.OWNER,
            is_active=True
        )
        try:
            user = await self.user_repo.add(user)
            await self.session.commit()
        except Exception as exc:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        return user

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Rotate access token using valid refresh token."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            
            user_id = uuid.UUID(payload.get("sub"))
            merchant_id = uuid.UUID(payload.get("merchant_id"))
        except Exception:
            # Fallback if refresh token decoding fails
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active or str(user.merchant_id) != str(merchant_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User or merchant not active")

        new_access_token = create_access_token(subject=str(user.id), merchant_id=str(user.merchant_id))
        new_refresh_token = create_refresh_token(subject=str(user.id), merchant_id=str(user.merchant_id))

        return TokenResponse(
            access_token=new_access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=new_refresh_token
        )

    async def create_demo_merchant_owner_if_not_exists(self, email: str, password: str, merchant_name: str) -> MerchantUser:
        """Helper for seeding demo merchant owner user."""
        clean_email = email.strip().lower()
        try:
            existing_user = await self.user_repo.get_by_email(clean_email)
            if existing_user:
                return existing_user
        except Exception:
            pass

        merchant = Merchant(
            id=DEMO_MERCHANT_ID,
            name=merchant_name,
            razorpay_key_id=settings.RAZORPAY_KEY_ID,
            razorpay_key_secret_enc=encrypt_secret(settings.RAZORPAY_KEY_SECRET),
            razorpay_webhook_secret_enc=encrypt_secret(settings.RAZORPAY_WEBHOOK_SECRET)
        )
        try:
            merchant = await self.merchant_repo.add(merchant)
        except Exception:
            pass

        user = MerchantUser(
            id=DEMO_USER_ID,
            merchant_id=merchant.id if merchant else DEMO_MERCHANT_ID,
            email=clean_email,
            password_hash=get_password_hash(password),
            role=UserRole.OWNER,
            is_active=True
        )
        try:
            user = await self.user_repo.add(user)
            await self.session.commit()
        except Exception:
            pass
        return user

    async def register_user(self, payload: RegisterRequest) -> Tuple[TokenResponse, MerchantUser]:
        """Register a new merchant account and user profile."""
        clean_email = payload.email.strip().lower()

        existing = await self.user_repo.get_by_email(clean_email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        user_id = uuid.uuid4()
        user = await self.provision_merchant_and_user(
            user_id=user_id,
            email=clean_email,
            password=payload.password,
            merchant_name=payload.merchant_name
        )

        access_token = create_access_token(
            subject=str(user.id),
            merchant_id=str(user.merchant_id)
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            merchant_id=str(user.merchant_id)
        )

        user_info = UserResponse(
            id=user.id,
            merchant_id=user.merchant_id,
            email=user.email,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            is_active=user.is_active
        )

        token_response = TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token,
            user=user_info
        )
        return token_response, user
