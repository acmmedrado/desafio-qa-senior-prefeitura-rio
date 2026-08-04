import pytest

from tests.data import FAVORITE_SERVICE_TITLE, SERVICE_UPDATED_EVENT, VACCINATION_SERVICE_ID
from tests.helpers import build_signed_webhook_request


def service_fingerprint(services):
    return sorted((service["id"], service["view_count"], service["active"]) for service in services)


@pytest.mark.contract
@pytest.mark.data_management
def test_catalog_snapshot_fixture_returns_fresh_copy(catalog_snapshot):
    original_first_title = catalog_snapshot[0]["title"]

    catalog_snapshot[0]["title"] = "mutated inside this test"

    assert original_first_title != catalog_snapshot[0]["title"]


@pytest.mark.contract
@pytest.mark.data_management
def test_catalog_snapshot_is_not_shared_between_tests(catalog_snapshot):
    assert catalog_snapshot[0]["title"] != "mutated inside this test"


@pytest.mark.contract
@pytest.mark.data_management
def test_favorite_does_not_mutate_shared_catalog_state(
    api, auth_headers, catalog, catalog_snapshot
):
    service = catalog.by_title(FAVORITE_SERVICE_TITLE)
    before = service_fingerprint(catalog_snapshot)

    response = api.favorite(
        service["id"],
        headers=auth_headers,
    )
    after_response = api.list_services(per_page=100)

    assert response.status_code == 200
    assert service_fingerprint(after_response.json()["data"]) == before


@pytest.mark.contract
@pytest.mark.data_management
def test_webhook_does_not_mutate_shared_catalog_state(api, catalog_snapshot):
    before = service_fingerprint(catalog_snapshot)
    body, headers = build_signed_webhook_request(
        {"event": SERVICE_UPDATED_EVENT, "id": VACCINATION_SERVICE_ID}
    )

    response = api.webhook(
        data=body,
        headers=headers,
    )
    after_response = api.list_services(per_page=100)

    assert response.status_code == 200
    assert service_fingerprint(after_response.json()["data"]) == before
