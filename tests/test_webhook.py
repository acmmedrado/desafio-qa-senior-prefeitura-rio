import json

import pytest

from tests.helpers import webhook_signature


@pytest.mark.contract
def test_webhook_accepts_valid_hmac_signature(api):
    payload = {"event": "service.updated", "id": "s002", "active": True}
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": webhook_signature(body),
        },
        timeout=3,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.negative
def test_webhook_rejects_invalid_json(api):
    response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        data="{not-json",
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": "sha256=invalid",
        },
        timeout=3,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid JSON payload"


@pytest.mark.negative
@pytest.mark.known_bug
def test_webhook_rejects_missing_signature(api):
    response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        json={"event": "service.deleted", "id": "s002"},
        timeout=3,
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid webhook signature"


@pytest.mark.negative
@pytest.mark.known_bug
def test_webhook_rejects_invalid_signature(api):
    response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        json={"event": "service.deleted", "id": "s002"},
        headers={"X-Signature-256": "sha256=invalid"},
        timeout=3,
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid webhook signature"
