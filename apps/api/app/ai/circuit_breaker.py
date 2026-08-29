from datetime import datetime, timezone, timedelta
from typing import Optional

class AICircuitBreaker:
    """
    AI Provider Circuit Breaker (§36).
    Protects against downstream OpenAI outages and retry storms.
    """
    def __init__(
        self,
        failure_threshold: int = 5,
        cooldown_minutes: int = 15
    ):
        self.failure_threshold = failure_threshold
        self.cooldown_minutes = cooldown_minutes
        self.consecutive_failures = 0
        self.tripped_at: Optional[datetime] = None

    def is_tripped(self) -> bool:
        """Check if circuit breaker is active and open."""
        if not self.tripped_at:
            return False

        elapsed = datetime.now(timezone.utc) - self.tripped_at
        if elapsed > timedelta(minutes=self.cooldown_minutes):
            # Cooldown passed -> reset breaker
            self.reset()
            return False

        return True

    def record_success(self):
        """Record successful call and reset failure counter."""
        self.consecutive_failures = 0
        self.tripped_at = None

    def record_failure(self):
        """Record failure and trip breaker if threshold exceeded."""
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.tripped_at = datetime.now(timezone.utc)

    def reset(self):
        """Explicitly reset circuit breaker state."""
        self.consecutive_failures = 0
        self.tripped_at = None

# Global instance for AI client layer
global_ai_circuit_breaker = AICircuitBreaker()
