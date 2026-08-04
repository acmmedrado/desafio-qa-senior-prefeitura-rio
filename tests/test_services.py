import pytest


@pytest.mark.contract
@pytest.mark.known_bug
def test_list_services_default_pagination_contract(api):
    response = api.get(f"{api.base_url}/api/v1/services", timeout=3)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 11
    assert body["page"] == 1
    assert body["per_page"] == 10
    assert body["total_pages"] == 2
    assert len(body["data"]) == 10


@pytest.mark.contract
def test_list_services_second_page_has_remaining_item(api):
    response = api.get(f"{api.base_url}/api/v1/services?page=2&per_page=10", timeout=3)

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == "s011"


@pytest.mark.contract
@pytest.mark.known_bug
def test_list_services_total_pages_uses_ceiling_for_smaller_page_size(api):
    response = api.get(f"{api.base_url}/api/v1/services?page=1&per_page=5", timeout=3)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 11
    assert body["per_page"] == 5
    assert body["total_pages"] == 3


@pytest.mark.contract
def test_list_services_page_beyond_range_returns_empty_data(api):
    response = api.get(f"{api.base_url}/api/v1/services?page=99&per_page=10", timeout=3)

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 99
    assert body["data"] == []
    assert body["total"] == 11


@pytest.mark.negative
def test_list_services_invalid_pagination_values_fall_back_to_safe_defaults(api):
    response = api.get(f"{api.base_url}/api/v1/services?page=-5&per_page=999", timeout=3)

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["per_page"] == 10
    assert len(body["data"]) == 10


@pytest.mark.contract
def test_get_existing_service_by_id(api):
    response = api.get(f"{api.base_url}/api/v1/services/s002", timeout=3)

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
    assert body["id"] == "s002"
    assert body["title"] == "Vacinação Gratuita"
    assert body["category"] == "saude"
    assert isinstance(body["tags"], list)
    assert isinstance(body["view_count"], int)
    assert body["active"] is True


@pytest.mark.negative
@pytest.mark.known_bug
def test_get_unknown_service_returns_404_instead_of_server_error(api):
    response = api.get(f"{api.base_url}/api/v1/services/s999", timeout=3)

    assert response.status_code == 404
    assert response.json()["error"] == "service not found"
