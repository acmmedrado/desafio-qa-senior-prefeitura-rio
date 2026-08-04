import pytest

from tests.data import ADVERSARIAL_UNKNOWN_SERVICE_IDS, VACCINATION_SERVICE_TITLE


@pytest.mark.contract
@pytest.mark.known_bug
def test_list_services_default_pagination_contract(api, catalog_snapshot):
    response = api.list_services()

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == len(catalog_snapshot)
    assert body["page"] == 1
    assert body["per_page"] == 10
    assert body["total_pages"] == 2
    assert len(body["data"]) == 10


@pytest.mark.contract
def test_list_services_second_page_has_remaining_item(api, catalog_snapshot):
    response = api.list_services(page=2, per_page=10)

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert len(body["data"]) == max(len(catalog_snapshot) - 10, 0)
    assert body["data"][0]["id"] == catalog_snapshot[10]["id"]


@pytest.mark.contract
@pytest.mark.known_bug
def test_list_services_total_pages_uses_ceiling_for_smaller_page_size(api, catalog_snapshot):
    response = api.list_services(page=1, per_page=5)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == len(catalog_snapshot)
    assert body["per_page"] == 5
    assert body["total_pages"] == 3


@pytest.mark.contract
def test_list_services_page_beyond_range_returns_empty_data(api, catalog_snapshot):
    response = api.list_services(page=99, per_page=10)

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 99
    assert body["data"] == []
    assert body["total"] == len(catalog_snapshot)


@pytest.mark.negative
def test_list_services_invalid_pagination_values_fall_back_to_safe_defaults(api):
    response = api.list_services(page=-5, per_page=999)

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["per_page"] == 10
    assert len(body["data"]) == 10


@pytest.mark.negative
def test_list_services_zero_pagination_values_fall_back_to_safe_defaults(api):
    response = api.list_services(page=0, per_page=0)

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["per_page"] == 10
    assert len(body["data"]) == 10


@pytest.mark.negative
def test_list_services_non_numeric_pagination_values_fall_back_to_safe_defaults(api):
    response = api.list_services_raw("page=abc&per_page=xyz")

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["per_page"] == 10
    assert len(body["data"]) == 10


@pytest.mark.contract
def test_get_existing_service_by_id(api, catalog):
    service = catalog.by_title(VACCINATION_SERVICE_TITLE)
    response = api.get_service(service["id"])

    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {
        "id",
        "title",
        "description",
        "category",
        "tags",
        "organization",
        "view_count",
        "active",
    }
    assert body["id"] == service["id"]
    assert body["title"] == service["title"]
    assert body["category"] == service["category"]
    assert isinstance(body["tags"], list)
    assert isinstance(body["view_count"], int)
    assert body["active"] is True


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
def test_get_unknown_service_returns_404_instead_of_server_error(api, catalog):
    response = api.get_service(catalog.unknown_id())

    assert response.status_code == 404
    assert response.json()["error"] == "service not found"


@pytest.mark.negative
@pytest.mark.known_bug
@pytest.mark.known_bug_high
def test_get_unknown_service_handles_adversarial_ids_without_server_error(api):
    responses = [
        (service_id, api.get_service(service_id).status_code)
        for service_id in ADVERSARIAL_UNKNOWN_SERVICE_IDS
    ]

    assert responses == [(service_id, 404) for service_id in ADVERSARIAL_UNKNOWN_SERVICE_IDS]
