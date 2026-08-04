import hashlib
import hmac
import json
import os

WEBHOOK_SECRET = "webhook-secret-2024"


def webhook_signature(body: bytes, secret: str = WEBHOOK_SECRET) -> str:
    secret = os.getenv("WEBHOOK_SECRET", secret)
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def build_signed_webhook_request(payload):
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": webhook_signature(body),
    }
    return body, headers
