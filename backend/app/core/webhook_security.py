import hmac
import hashlib


def generate_webhook_signature(payload: bytes, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()


def verify_webhook_signature(
    payload: bytes,
    secret: str,
    received_signature: str
) -> bool:
    expected_signature = generate_webhook_signature(
        payload,
        secret
    )

    return hmac.compare_digest(
        expected_signature,
        received_signature
    )