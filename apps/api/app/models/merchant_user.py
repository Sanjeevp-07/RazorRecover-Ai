import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
import enum

class UserRole(str, enum.Enum):
    OWNER = "owner"
    REVIEWER = "reviewer"

class MerchantUser(Base):
    __tablename__ = "merchant_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="user_role_enum"), default=UserRole.OWNER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    merchant = relationship("Merchant", back_populates="users")
