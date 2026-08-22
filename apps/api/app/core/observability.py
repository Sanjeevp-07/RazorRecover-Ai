import json
import logging
import time
from typing import Dict, Any, Optional
import contextvars

# Context variables for request tracing (§22)
correlation_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("correlation_id", default=None)
merchant_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("merchant_id", default=None)

# Enumerated Error Categories (§22)
class ErrorCategory:
    AI_UNAVAILABLE = "ai_unavailable"
    PROVIDER_TIMEOUT = "provider_timeout"
    MALFORMED_OUTPUT = "malformed_output"
    POLICY_ERROR = "policy_error"
    VALIDATION_ERROR = "validation_error"

# In-memory Prometheus-compatible Metric Registry (§22)
class MetricRegistry:
    def __init__(self):
        self.webhook_events_total: Dict[str, int] = {}
        self.ai_calls_total: Dict[str, int] = {}
        self.policy_decisions_total: Dict[str, int] = {}
        self.action_executions_total: Dict[str, int] = {}
        self.celery_task_duration_seconds: Dict[str, float] = {}

    def inc_webhook_event(self, event_type: str):
        self.webhook_events_total[event_type] = self.webhook_events_total.get(event_type, 0) + 1

    def inc_ai_call(self, model: str, status: str):
        key = f'model="{model}",status="{status}"'
        self.ai_calls_total[key] = self.ai_calls_total.get(key, 0) + 1

    def inc_policy_decision(self, decision: str):
        self.policy_decisions_total[decision] = self.policy_decisions_total.get(decision, 0) + 1

    def inc_action_execution(self, tool: str, status: str):
        key = f'tool="{tool}",status="{status}"'
        self.action_executions_total[key] = self.action_executions_total.get(key, 0) + 1

    def record_celery_task_duration(self, task_name: str, duration: float):
        self.celery_task_duration_seconds[task_name] = duration

    def generate_prometheus_metrics(self) -> str:
        """Render Prometheus exposition format (§22)."""
        lines = []

        lines.append("# HELP webhook_events_total Total webhook events received by type")
        lines.append("# TYPE webhook_events_total counter")
        for event_type, count in sorted(self.webhook_events_total.items()):
            lines.append(f'webhook_events_total{{event_type="{event_type}"}} {count}')

        lines.append("# HELP ai_calls_total Total AI model reasoning invocations")
        lines.append("# TYPE ai_calls_total counter")
        for key, count in sorted(self.ai_calls_total.items()):
            lines.append(f"ai_calls_total{{{key}}} {count}")

        lines.append("# HELP policy_decisions_total Total policy guardrail decisions evaluated")
        lines.append("# TYPE policy_decisions_total counter")
        for decision, count in sorted(self.policy_decisions_total.items()):
            lines.append(f'policy_decisions_total{{decision="{decision}"}} {count}')

        lines.append("# HELP action_executions_total Total recovery actions executed by tool and status")
        lines.append("# TYPE action_executions_total counter")
        for key, count in sorted(self.action_executions_total.items()):
            lines.append(f"action_executions_total{{{key}}} {count}")

        lines.append("# HELP celery_task_duration_seconds Duration of async worker task executions in seconds")
        lines.append("# TYPE celery_task_duration_seconds gauge")
        for task, duration in sorted(self.celery_task_duration_seconds.items()):
            lines.append(f'celery_task_duration_seconds{{task="{task}"}} {duration:.4f}')

        return "\n".join(lines) + "\n"

metrics = MetricRegistry()

class StructuredJsonFormatter(logging.Formatter):
    """Structured JSON logging formatter carrying correlation_id and merchant_id (§22)."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": correlation_id_ctx.get() or "system",
            "merchant_id": merchant_id_ctx.get() or "system",
            "event_type": getattr(record, "event_type", "APP_EVENT"),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)
