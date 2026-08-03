import pytest


@pytest.mark.contract
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
    assert body["id"] == "s002"
    assert body["title"] == "Vacinação Gratuita"
    assert body["category"] == "saude"


@pytest.mark.negative
@pytest.mark.known_bug
def test_get_unknown_service_returns_404_instead_of_server_error(api):
    response = api.get(f"{api.base_url}/api/v1/services/s999", timeout=3)

    assert response.status_code == 404
    assert response.json()["error"] == "service not found"
