import pytest


@pytest.mark.negative
def test_favorite_requires_authorization(api):
    response = api.post(f"{api.base_url}/api/v1/services/s001/favorite", timeout=3)

    assert response.status_code == 401
    assert response.json()["error"] == "missing authorization header"


@pytest.mark.negative
def test_favorite_rejects_invalid_token(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/s001/favorite",
        headers={"Authorization": "Bearer wrong-token"},
        timeout=3,
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid token"


@pytest.mark.negative
def test_favorite_rejects_malformed_authorization_scheme(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/s001/favorite",
        headers={"Authorization": "Token qa-challenge-token"},
        timeout=3,
    )

    assert response.status_code == 401
    assert response.json()["error"] == "missing authorization header"


@pytest.mark.contract
def test_favorite_accepts_valid_token(api, auth_headers):
    response = api.post(
        f"{api.base_url}/api/v1/services/s001/favorite",
        headers=auth_headers,
        timeout=3,
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "added to favorites",
        "service_id": "s001",
    }


@pytest.mark.negative
def test_favorite_unknown_service_returns_404(api, auth_headers):
    response = api.post(
        f"{api.base_url}/api/v1/services/s999/favorite",
        headers=auth_headers,
        timeout=3,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "service not found"


@pytest.mark.negative
@pytest.mark.known_bug
def test_recommendations_requires_authorization(api):
    response = api.get(f"{api.base_url}/api/v1/services/s002/recommendations", timeout=3)

    assert response.status_code == 401
    assert response.json()["error"] == "missing authorization header"


@pytest.mark.contract
def test_recommendations_returns_same_category_services_when_authorized(api, auth_headers):
    response = api.get(
        f"{api.base_url}/api/v1/services/s002/recommendations",
        headers=auth_headers,
        timeout=3,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["service_id"] == "s002"
    assert all(item["category"] == "saude" for item in body["recommendations"])
    assert all(item["id"] != "s002" for item in body["recommendations"])


@pytest.mark.negative
def test_recommendations_unknown_service_returns_404_when_authorized(api, auth_headers):
    response = api.get(
        f"{api.base_url}/api/v1/services/s999/recommendations",
        headers=auth_headers,
        timeout=3,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "service not found"
