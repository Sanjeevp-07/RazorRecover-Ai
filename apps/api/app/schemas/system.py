from datetime import datetime, timezone
from typing import List, Optional
from app.schemas.base import BaseSchema

class SystemRoadmapItem(BaseSchema):
    """System completion item detail (§42)."""
    feature_name: str
    section_reference: str
    status: str  # "COMPLETED", "IN_PROGRESS", "PLANNED"
    completion_percentage: float
    description: str

class SystemRoadmapResponse(BaseSchema):
    """System completion status response (§42)."""
    overall_completion_pct: float = 100.0
    current_version: str = "3.0.0"
    built_modules_count: int = 44
    items: List[SystemRoadmapItem]

class SystemResilienceMetric(BaseSchema):
    """Component resilience health metric (§43)."""
    component: str
    status: str  # "HEALTHY", "DEGRADED", "DISABLED"
    circuit_breaker_active: bool = False
    fallback_mode_enabled: bool = False
    details: Optional[str] = None

class SystemResilienceResponse(BaseSchema):
    """Real-world resilience matrix response (§43)."""
    environment: str
    overall_resilience_status: str
    checked_at: datetime
    metrics: List[SystemResilienceMetric]

class SystemExclusionItem(BaseSchema):
    """Explicit v3 Exclusion item (§44)."""
    exclusion_code: str
    title: str
    rationale: str
    enforcement: str

class SystemExclusionsResponse(BaseSchema):
    """Explicit v3 Exclusions response (§44)."""
    version: str = "3.0.0"
    governance_framework: str = "RazorRecover Enterprise Safety & Governance Framework"
    exclusions: List[SystemExclusionItem]
