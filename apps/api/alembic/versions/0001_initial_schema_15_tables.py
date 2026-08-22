"""0001_initial_schema_15_tables

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-22 12:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Enum Types
    user_role_enum = postgresql.ENUM('owner', 'reviewer', name='user_role_enum')
    user_role_enum.create(op.get_bind(), checkfirst=True)

    order_status_enum = postgresql.ENUM('created', 'attempted', 'paid', name='order_status_enum')
    order_status_enum.create(op.get_bind(), checkfirst=True)

    payment_status_enum = postgresql.ENUM('created', 'attempted', 'failed', 'captured', 'recovered', name='payment_status_enum')
    payment_status_enum.create(op.get_bind(), checkfirst=True)

    webhook_status_enum = postgresql.ENUM('received', 'processed', 'failed', name='webhook_processing_status_enum')
    webhook_status_enum.create(op.get_bind(), checkfirst=True)

    case_status_enum = postgresql.ENUM('OPEN', 'ANALYZING', 'DENIED', 'PENDING_APPROVAL', 'EXECUTING', 'RECOVERED', 'CLOSED', 'EXPIRED', name='recovery_case_status_enum')
    case_status_enum.create(op.get_bind(), checkfirst=True)

    policy_outcome_enum = postgresql.ENUM('ALLOW', 'DENY', 'HUMAN_APPROVAL', name='policy_outcome_enum')
    policy_outcome_enum.create(op.get_bind(), checkfirst=True)

    action_status_enum = postgresql.ENUM('PENDING', 'IN_PROGRESS', 'SUCCEEDED', 'FAILED', 'RETRYING', name='action_execution_status_enum')
    action_status_enum.create(op.get_bind(), checkfirst=True)

    approval_status_enum = postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED', name='approval_status_enum')
    approval_status_enum.create(op.get_bind(), checkfirst=True)

    notification_channel_enum = postgresql.ENUM('email', 'sms', name='notification_channel_enum')
    notification_channel_enum.create(op.get_bind(), checkfirst=True)

    notification_status_enum = postgresql.ENUM('queued', 'sent', 'failed', name='notification_status_enum')
    notification_status_enum.create(op.get_bind(), checkfirst=True)

    # 6.1 merchants
    op.create_table(
        'merchants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('razorpay_key_id', sa.Text(), nullable=False),
        sa.Column('razorpay_key_secret_enc', sa.Text(), nullable=False),
        sa.Column('razorpay_webhook_secret_enc', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 6.2 merchant_users
    op.create_table(
        'merchant_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchants.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('email', sa.Text(), unique=True, nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('role', user_role_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_merchant_users_merchant_id', 'merchant_users', ['merchant_id'])

    # 6.3 customers
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchants.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('provider_customer_id', sa.Text(), nullable=True),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('phone', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_customers_merchant_id', 'customers', ['merchant_id'])

    # 6.4 orders
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchants.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('provider_order_id', sa.Text(), unique=True, nullable=False),
        sa.Column('amount_minor', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', order_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_orders_merchant_id', 'orders', ['merchant_id'])

    # 6.5 payments
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchants.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('provider_payment_id', sa.Text(), unique=True, nullable=False),
        sa.Column('amount_minor', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', payment_status_enum, nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('method', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_payments_merchant_id', 'payments', ['merchant_id'])

    # 6.6 webhook_events
    op.create_table(
        'webhook_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchants.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('external_event_id', sa.Text(), unique=True, nullable=False),
        sa.Column('event_type', sa.Text(), nullable=False),
        sa.Column('raw_payload', postgresql.JSONB(), nullable=False),
        sa.Column('processing_status', webhook_status_enum, nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('ix_webhook_events_merchant_id', 'webhook_events', ['merchant_id'])

    # 6.7 recovery_cases
    op.create_table(
        'recovery_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchants.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payments.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('status', case_status_enum, nullable=False),
        sa.Column('correlation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_recovery_cases_merchant_id', 'recovery_cases', ['merchant_id'])
    op.create_index('ix_recovery_cases_payment_id', 'recovery_cases', ['payment_id'])
    op.create_index('ix_recovery_cases_status', 'recovery_cases', ['status'])

    # 6.8 risk_signals
    op.create_table(
        'risk_signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recovery_cases.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('customer_history_score', sa.Numeric(precision=4, scale=3), nullable=False),
        sa.Column('velocity_flag', sa.Boolean(), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_risk_signals_case_id', 'risk_signals', ['case_id'])

    # 6.9 ai_decisions
    op.create_table(
        'ai_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recovery_cases.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('model_id', sa.Text(), nullable=False),
        sa.Column('schema_version', sa.Text(), nullable=False),
        sa.Column('raw_output', postgresql.JSONB(), nullable=False),
        sa.Column('validated_output', postgresql.JSONB(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_ai_decisions_case_id', 'ai_decisions', ['case_id'])

    # 6.10 policy_decisions
    op.create_table(
        'policy_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recovery_cases.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('ai_decision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_decisions.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('decision', policy_outcome_enum, nullable=False),
        sa.Column('policy_version', sa.Text(), nullable=False),
        sa.Column('matched_rule', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_policy_decisions_case_id', 'policy_decisions', ['case_id'])

    # 6.11 policy_config
    op.create_table(
        'policy_config',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchants.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('key', sa.Text(), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    # Seed default policy configurations (§6.11)
    op.execute("""
        INSERT INTO policy_config (id, merchant_id, key, value, updated_at) VALUES
        (gen_random_uuid(), NULL, 'approval_amount_threshold_minor', '5000000', NOW()),
        (gen_random_uuid(), NULL, 'approval_risk_threshold', '0.7', NOW()),
        (gen_random_uuid(), NULL, 'retry_count_limit', '3', NOW()),
        (gen_random_uuid(), NULL, 'approval_sla_hours', '24', NOW());
    """)

    # 6.12 action_executions
    op.create_table(
        'action_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recovery_cases.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('tool_name', sa.Text(), nullable=False),
        sa.Column('idempotency_key', sa.Text(), unique=True, nullable=False),
        sa.Column('status', action_status_enum, nullable=False),
        sa.Column('input_payload', postgresql.JSONB(), nullable=True),
        sa.Column('output_payload', postgresql.JSONB(), nullable=True),
        sa.Column('error_category', sa.Text(), nullable=True),
        sa.Column('attempt_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_action_executions_case_id', 'action_executions', ['case_id'])

    # 6.13 approvals
    op.create_table(
        'approvals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recovery_cases.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('status', approval_status_enum, nullable=False),
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sla_expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('decided_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchant_users.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('decision_note', sa.Text(), nullable=True)
    )
    op.create_index('ix_approvals_case_id', 'approvals', ['case_id'])

    # 6.14 audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('merchant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('merchants.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('correlation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.Text(), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_audit_logs_merchant_id', 'audit_logs', ['merchant_id'])
    op.create_index('ix_audit_logs_correlation_id', 'audit_logs', ['correlation_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # 6.15 notifications
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('recovery_cases.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('channel', notification_channel_enum, nullable=False),
        sa.Column('template', sa.Text(), nullable=False),
        sa.Column('status', notification_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('ix_notifications_case_id', 'notifications', ['case_id'])

def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('audit_logs')
    op.drop_table('approvals')
    op.drop_table('action_executions')
    op.drop_table('policy_config')
    op.drop_table('policy_decisions')
    op.drop_table('ai_decisions')
    op.drop_table('risk_signals')
    op.drop_table('recovery_cases')
    op.drop_table('webhook_events')
    op.drop_table('payments')
    op.drop_table('orders')
    op.drop_table('customers')
    op.drop_table('merchant_users')
    op.drop_table('merchants')
