import hmac
import hashlib
import pytest
from app.integrations.razorpay.webhook import verify_razorpay_signature

def test_razorpay_webhook_signature_verification():
    secret = "rzp_webhook_secret_key_123"
    raw_body = b'{"event":"payment.failed","payload":{"payment":{"entity":{"id":"pay_12345"}}}}'

    # Compute valid HMAC-SHA256 signature
    valid_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    assert verify_razorpay_signature(raw_body, valid_signature, secret) is True

def test_razorpay_webhook_invalid_signature_rejection():
    secret = "rzp_webhook_secret_key_123"
    raw_body = b'{"event":"payment.failed"}'
    invalid_signature = "invalid_signature_hash"

    assert verify_razorpay_signature(raw_body, invalid_signature, secret) is False

def test_razorpay_webhook_tampered_payload_rejection():
    secret = "rzp_webhook_secret_key_123"
    raw_body = b'{"event":"payment.failed"}'
    tampered_body = b'{"event":"payment.failed","tampered":true}'

    valid_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    assert verify_razorpay_signature(tampered_body, valid_signature, secret) is False
