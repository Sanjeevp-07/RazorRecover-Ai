"""
Repositories Layer.
Responsibility: Database access only. No business rules, no policy checks.
Must filter by merchant_id in all queries.
Forbidden imports: app.services, app.api, app.policy, app.ai, app.tools
"""
