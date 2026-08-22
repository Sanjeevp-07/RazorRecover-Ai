"""
Services Layer.
Responsibility: Business workflow orchestration.
The only layer allowed to call Policy, AI, and multiple repositories in one operation.
Forbidden imports: app.api (routers)
"""
