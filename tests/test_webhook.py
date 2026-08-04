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


@pytest.mark.contract
def test_webhook_accepts_large_valid_payload(api):
    payload = {"event": "service.bulk_updated", "ids": [f"s{i:03d}" for i in range(1, 201)]}
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


@pytest.mark.contract
def test_webhook_replay_with_same_signature_is_currently_accepted(api):
    payload = {"event": "service.updated", "id": "s002", "nonce": "replay-check"}
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": webhook_signature(body),
    }

    first_response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        data=body,
        headers=headers,
        timeout=3,
    )
    second_response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        data=body,
        headers=headers,
        timeout=3,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200


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


@pytest.mark.negative
@pytest.mark.known_bug
def test_webhook_rejects_signature_from_different_payload(api):
    signed_body = json.dumps({"event": "service.updated", "id": "s002"}).encode("utf-8")

    response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        json={"event": "service.deleted", "id": "s002"},
        headers={"X-Signature-256": webhook_signature(signed_body)},
        timeout=3,
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid webhook signature"
