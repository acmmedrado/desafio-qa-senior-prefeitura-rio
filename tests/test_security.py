import pytest

from tests.data import FAVORITE_SERVICE_ID

INJECTION_SEARCH_PAYLOADS = [
    "' OR '1'='1",
    '{"$ne": null}',
    "<script>alert(1)</script>",
    "../../etc/passwd",
    ";cat /etc/passwd",
]

ENCODED_ADVERSARIAL_SERVICE_PATHS = [
    "/api/v1/services/%27%20OR%20%271%27%3D%271",
    "/api/v1/services/s002%00.json",
]

SENSITIVE_ERROR_TOKENS = [
    "panic",
    "runtime error",
    "stack trace",
    "webhook-secret-2024",
    "qa-challenge-token",
    "/Users/",
    "/home/",
    "/go/pkg/mod/",
]


def assert_no_sensitive_error_details(response):
    body = response.text.lower()

    assert "webhook-secret-2024" not in response.text
    assert "qa-challenge-token" not in response.text
    assert all(token.lower() not in body for token in SENSITIVE_ERROR_TOKENS)


@pytest.mark.negative
@pytest.mark.security
def test_search_handles_injection_payloads_without_server_error(api):
    responses = [api.search(payload) for payload in INJECTION_SEARCH_PAYLOADS]

    assert all(response.status_code in {200, 400} for response in responses)
    assert all(response.status_code < 500 for response in responses)
    for response in responses:
        assert_no_sensitive_error_details(response)


@pytest.mark.negative
@pytest.mark.security
def test_search_escapes_script_payload_in_json_response(api):
    response = api.search("<script>alert(1)</script>")

    assert response.status_code == 200
    assert "<script>" not in response.text
    assert "</script>" not in response.text


@pytest.mark.negative
@pytest.mark.security
def test_service_detail_rejects_encoded_path_traversal_without_sensitive_disclosure(api):
    response = api.request("GET", "/api/v1/services/..%2F..%2Fetc%2Fpasswd")

    assert response.status_code in {400, 404}
    assert_no_sensitive_error_details(response)


@pytest.mark.negative
@pytest.mark.security
def test_favorite_rejects_oversized_bearer_token(api):
    response = api.favorite(
        FAVORITE_SERVICE_ID,
        headers={"Authorization": f"Bearer {'A' * 5000}"},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid token"
    assert_no_sensitive_error_details(response)


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
@pytest.mark.security
def test_webhook_rejects_malformed_signature_scheme(api):
    response = api.webhook(
        json={"event": "service.deleted", "id": FAVORITE_SERVICE_ID},
        headers={"X-Signature-256": "md5=not-allowed"},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid webhook signature"


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
@pytest.mark.security
def test_service_detail_handles_encoded_injection_ids_without_server_error(api):
    responses = [api.request("GET", path) for path in ENCODED_ADVERSARIAL_SERVICE_PATHS]

    assert all(response.status_code in {400, 404} for response in responses)
    for response in responses:
        assert_no_sensitive_error_details(response)
