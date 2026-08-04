import hashlib
import hmac
import os

WEBHOOK_SECRET = "webhook-secret-2024"


def webhook_signature(body: bytes, secret: str = WEBHOOK_SECRET) -> str:
    secret = os.getenv("WEBHOOK_SECRET", secret)
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"
