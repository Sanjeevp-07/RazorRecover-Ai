from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """
    Base Pydantic schema enforcing extra="forbid" strictly across all request,
    response, AI, policy, and tool payload models (per §3 and §5 of spec).
    Unknown or unhandled fields will be rejected automatically.
    """
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        from_attributes=True
    )
