import hmac
import hashlib

def verify_razorpay_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    """
    Verify Razorpay HMAC-SHA256 webhook signature against raw request body (§10.2).
    """
    if not signature or not secret or not raw_body:
        return False

    expected_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature.lower(), signature.lower())
