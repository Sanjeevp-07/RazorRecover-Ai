import pytest
from app.services.state_machine import StateMachineManager
from app.models.payment import PaymentStatus
from app.models.recovery_case import RecoveryCaseStatus

def test_payment_state_machine_transitions():
    mgr = StateMachineManager(session=None)
    
    # Valid transitions (§8.1)
    assert mgr.validate_payment_transition(PaymentStatus.CREATED, PaymentStatus.ATTEMPTED) is True
    assert mgr.validate_payment_transition(PaymentStatus.ATTEMPTED, PaymentStatus.FAILED) is True
    assert mgr.validate_payment_transition(PaymentStatus.ATTEMPTED, PaymentStatus.CAPTURED) is True
    assert mgr.validate_payment_transition(PaymentStatus.FAILED, PaymentStatus.RECOVERED) is True
    
    # Invalid transitions (§8.1)
    assert mgr.validate_payment_transition(PaymentStatus.CAPTURED, PaymentStatus.FAILED) is False
    assert mgr.validate_payment_transition(PaymentStatus.RECOVERED, PaymentStatus.FAILED) is False

def test_recovery_case_state_machine_transitions():
    mgr = StateMachineManager(session=None)
    
    # Valid transitions (§8.2)
    assert mgr.validate_case_transition(RecoveryCaseStatus.OPEN, RecoveryCaseStatus.ANALYZING) is True
    assert mgr.validate_case_transition(RecoveryCaseStatus.ANALYZING, RecoveryCaseStatus.PENDING_APPROVAL) is True
    assert mgr.validate_case_transition(RecoveryCaseStatus.ANALYZING, RecoveryCaseStatus.EXECUTING) is True
    assert mgr.validate_case_transition(RecoveryCaseStatus.ANALYZING, RecoveryCaseStatus.DENIED) is True
    assert mgr.validate_case_transition(RecoveryCaseStatus.PENDING_APPROVAL, RecoveryCaseStatus.EXECUTING) is True
    assert mgr.validate_case_transition(RecoveryCaseStatus.EXECUTING, RecoveryCaseStatus.RECOVERED) is True
    
    # Invalid transitions (§8.2)
    assert mgr.validate_case_transition(RecoveryCaseStatus.CLOSED, RecoveryCaseStatus.ANALYZING) is False
    assert mgr.validate_case_transition(RecoveryCaseStatus.DENIED, RecoveryCaseStatus.EXECUTING) is False
