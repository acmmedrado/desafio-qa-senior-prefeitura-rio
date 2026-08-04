import pytest

from tests.data import (
    SERVICE_DELETED_EVENT,
    SERVICE_UPDATED_EVENT,
    VACCINATION_SERVICE_ID,
    VACCINATION_SERVICE_TITLE,
)
from tests.helpers import build_signed_webhook_request, webhook_signature


@pytest.mark.contract
def test_webhook_accepts_valid_hmac_signature(api, catalog):
    service = catalog.by_title(VACCINATION_SERVICE_TITLE)
    payload = {"event": SERVICE_UPDATED_EVENT, "id": service["id"], "active": True}
    body, headers = build_signed_webhook_request(payload)

    response = api.webhook(
        data=body,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.contract
def test_webhook_accepts_large_valid_payload(api):
    payload = {"event": "service.bulk_updated", "ids": [f"s{i:03d}" for i in range(1, 201)]}
    body, headers = build_signed_webhook_request(payload)

    response = api.webhook(
        data=body,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.contract
def test_webhook_replay_with_same_signature_is_currently_accepted(api):
    payload = {
        "event": SERVICE_UPDATED_EVENT,
        "id": VACCINATION_SERVICE_ID,
        "nonce": "replay-check",
    }
    body, headers = build_signed_webhook_request(payload)

    first_response = api.webhook(
        data=body,
        headers=headers,
    )
    second_response = api.webhook(
        data=body,
        headers=headers,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200


@pytest.mark.negative
def test_webhook_rejects_invalid_json(api):
    body = b"{not-json"
    response = api.webhook(
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": webhook_signature(body),
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid JSON payload"


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
@pytest.mark.security
def test_webhook_rejects_missing_signature(api):
    response = api.webhook(
        json={"event": SERVICE_DELETED_EVENT, "id": VACCINATION_SERVICE_ID},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid webhook signature"


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
@pytest.mark.security
def test_webhook_rejects_invalid_signature(api):
    response = api.webhook(
        json={"event": SERVICE_DELETED_EVENT, "id": VACCINATION_SERVICE_ID},
        headers={"X-Signature-256": "sha256=invalid"},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid webhook signature"


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
@pytest.mark.security
def test_webhook_rejects_signature_created_with_wrong_secret(api):
    payload = {"event": SERVICE_DELETED_EVENT, "id": VACCINATION_SERVICE_ID}
    body, _headers = build_signed_webhook_request(payload)

    response = api.webhook(
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": webhook_signature(body, secret="wrong-secret"),
        },
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid webhook signature"


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
@pytest.mark.security
def test_webhook_rejects_signature_from_different_payload(api):
    signed_body, _headers = build_signed_webhook_request(
        {"event": SERVICE_UPDATED_EVENT, "id": VACCINATION_SERVICE_ID}
    )

    response = api.webhook(
        json={"event": SERVICE_DELETED_EVENT, "id": VACCINATION_SERVICE_ID},
        headers={"X-Signature-256": webhook_signature(signed_body)},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid webhook signature"
