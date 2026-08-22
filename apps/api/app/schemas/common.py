import uuid
from typing import Generic, TypeVar, List, Optional
from pydantic import Field
from app.schemas.base import BaseSchema

T = TypeVar("T")

class PaginatedResponse(BaseSchema, Generic[T]):
    """Standard Paginated List Envelope (§9.1)."""
    items: List[T]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)

class ErrorDetail(BaseSchema):
    """Error detail body."""
    code: str
    message: str
    correlation_id: Optional[str] = None

class ErrorEnvelope(BaseSchema):
    """Standard Error Envelope for 4xx/5xx responses (§9.1)."""
    error: ErrorDetail
