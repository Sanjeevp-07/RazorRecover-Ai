from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "razorrecover_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,  # §16.3: acks_late=True so a crashed worker re-delivers the task
    task_max_retries=3,
    task_routes={
        "app.workers.tasks.process_webhook_event": {"queue": "webhooks"},
        "app.workers.tasks.analyze_recovery_case": {"queue": "analysis"},
        "app.workers.tasks.send_notification": {"queue": "notifications"},
        "app.workers.tasks.expire_overdue_approvals": {"queue": "scheduled"},
    },
    beat_schedule={
        # §15 & §16.2: expire_overdue_approvals runs every 15 minutes
        "expire-overdue-approvals-every-15-min": {
            "task": "app.workers.tasks.expire_overdue_approvals",
            "schedule": 900.0  # 15 minutes in seconds
        }
    }
)
