import pytest

from tests.data import FAVORITE_SERVICE_TITLE, VACCINATION_SERVICE_ID, VACCINATION_SERVICE_TITLE


@pytest.mark.negative
def test_favorite_requires_authorization(api, catalog):
    service = catalog.by_title(FAVORITE_SERVICE_TITLE)
    response = api.favorite(service["id"])

    assert response.status_code == 401
    assert response.json()["error"] == "missing authorization header"


@pytest.mark.negative
def test_favorite_rejects_invalid_token(api, catalog):
    service = catalog.by_title(FAVORITE_SERVICE_TITLE)
    response = api.favorite(
        service["id"],
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid token"


@pytest.mark.negative
def test_favorite_rejects_malformed_authorization_scheme(api, catalog):
    service = catalog.by_title(FAVORITE_SERVICE_TITLE)
    response = api.favorite(
        service["id"],
        headers={"Authorization": "Token qa-challenge-token"},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "missing authorization header"


@pytest.mark.contract
def test_favorite_accepts_valid_token(api, auth_headers, catalog):
    service = catalog.by_title(FAVORITE_SERVICE_TITLE)
    response = api.favorite(
        service["id"],
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "added to favorites",
        "service_id": service["id"],
    }


@pytest.mark.negative
def test_favorite_unknown_service_returns_404(api, auth_headers, catalog):
    response = api.favorite(
        catalog.unknown_id(),
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "service not found"


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
@pytest.mark.security
def test_recommendations_requires_authorization(api):
    response = api.recommendations(VACCINATION_SERVICE_ID)

    assert response.status_code == 401
    assert response.json()["error"] == "missing authorization header"


@pytest.mark.contract
def test_recommendations_returns_same_category_services_when_authorized(api, auth_headers, catalog):
    service = catalog.by_title(VACCINATION_SERVICE_TITLE)
    response = api.recommendations(
        service["id"],
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["service_id"] == service["id"]
    assert all(item["category"] == service["category"] for item in body["recommendations"])
    assert all(item["id"] != service["id"] for item in body["recommendations"])


@pytest.mark.negative
def test_recommendations_unknown_service_returns_404_when_authorized(api, auth_headers, catalog):
    response = api.recommendations(
        catalog.unknown_id(),
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["error"] == "service not found"
