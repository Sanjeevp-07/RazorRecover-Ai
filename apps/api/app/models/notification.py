import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"

class NotificationStatus(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recovery_cases.id", ondelete="RESTRICT"), nullable=False, index=True)
    channel: Mapped[NotificationChannel] = mapped_column(SQLEnum(NotificationChannel, name="notification_channel_enum"), nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus, name="notification_status_enum"), default=NotificationStatus.QUEUED, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
