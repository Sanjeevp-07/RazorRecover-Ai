"""
Policy / Guardrail Engine Layer.
Responsibility: Deterministic authorization (§13). Pure function: (context) -> decision.
No I/O.
Forbidden imports: app.services, app.api, app.repositories, app.integrations, app.tools
"""
