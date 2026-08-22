"""
Tool Layer.
Responsibility: Validated action execution (§14).
The only layer permitted to call integrations for writes, and only after Policy = ALLOW.
Forbidden imports: app.services, app.api, app.policy, app.ai
"""
