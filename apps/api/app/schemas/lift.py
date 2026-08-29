from app.schemas.base import BaseSchema

class CausalLiftResponse(BaseSchema):
    """Schema for Causal Holdout Lift Analytics (§29)."""
    treatment_cases_count: int
    treatment_recovered_count: int
    recovered_rate_treatment: float
    control_cases_count: int
    control_recovered_count: int
    recovered_rate_control: float
    incremental_recovery_rate: float
    incremental_recovered_revenue_minor: int
    current_sample_size: int
    sample_size_sufficient: bool
    message: str
