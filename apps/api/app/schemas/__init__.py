"""
Pydantic Schemas Layer.
Responsibility: Request/response/domain schemas with extra="forbid".
"""
from app.schemas.base import BaseSchema

__all__ = ["BaseSchema"]
