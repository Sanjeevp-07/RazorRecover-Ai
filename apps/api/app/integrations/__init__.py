"""
Integrations Layer.
Responsibility: External provider HTTP calls only (Razorpay, Notifications).
Never called directly by a router or the AI layer.
Forbidden imports: app.services, app.api, app.repositories, app.policy, app.ai, app.tools
"""
