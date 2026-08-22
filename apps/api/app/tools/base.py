import uuid
import hashlib
from typing import Dict, Any, Tuple
from abc import ABC, abstractmethod

class BaseTool(ABC):
    """
    Base class for Tool Executor Layer (§14 & §17).
    Computes deterministic SHA256 idempotency keys for write actions:
    idempotency_key = sha256(case_id + tool_name + attempt_scope)
    """
    tool_name: str

    @staticmethod
    def generate_idempotency_key(case_id: uuid.UUID, tool_name: str, attempt_scope: str = "primary") -> str:
        """Compute SHA256 idempotency key (§14.1 & §17)."""
        raw_key = f"{case_id}:{tool_name}:{attempt_scope}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @abstractmethod
    async def execute(self, case_id: uuid.UUID, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Execute tool action.
        Returns (success: bool, output_payload: dict, error_category: str).
        """
        pass
