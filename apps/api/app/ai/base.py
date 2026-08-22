import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from app.ai.schemas import RecoveryRecommendation

class RecoveryReasoner(ABC):
    """
    Abstract AI Reasoner Interface (§11.2).
    Decouples application code from OpenAI or specific LLM provider implementations.
    Returns Tuple[Optional[RecoveryRecommendation], is_valid: bool, raw_output: str, latency_ms: int]
    """
    @abstractmethod
    async def analyze(
        self,
        case_id: uuid.UUID,
        context: Dict[str, Any]
    ) -> Tuple[Optional[RecoveryRecommendation], bool, str, int]:
        """
        Analyze recovery case context and produce a structured recommendation.
        If LLM call fails or output is malformed, returns (fallback_rec, False, raw_str, latency_ms).
        """
        pass
