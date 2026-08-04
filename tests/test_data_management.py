import json

import pytest

from tests.helpers import webhook_signature


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
    service = catalog.by_title("Cartão Rio")
    before = service_fingerprint(catalog_snapshot)

    response = api.post(
        f"{api.base_url}/api/v1/services/{service['id']}/favorite",
        headers=auth_headers,
        timeout=3,
    )
    after_response = api.get(f"{api.base_url}/api/v1/services?per_page=100", timeout=3)

    assert response.status_code == 200
    assert service_fingerprint(after_response.json()["data"]) == before


@pytest.mark.contract
@pytest.mark.data_management
def test_webhook_does_not_mutate_shared_catalog_state(api, catalog_snapshot):
    before = service_fingerprint(catalog_snapshot)
    body = json.dumps({"event": "service.updated", "id": "s002"}).encode("utf-8")

    response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": webhook_signature(body),
        },
        timeout=3,
    )
    after_response = api.get(f"{api.base_url}/api/v1/services?per_page=100", timeout=3)

    assert response.status_code == 200
    assert service_fingerprint(after_response.json()["data"]) == before
