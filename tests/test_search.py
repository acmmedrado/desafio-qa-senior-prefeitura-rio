import pytest


@pytest.mark.contract
def test_search_finds_services_by_text_case_insensitive(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "SAUDE"},
        timeout=3,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "SAUDE"
    assert body["total"] >= 2
    assert {item["id"] for item in body["results"]} >= {"s002", "s010"}


@pytest.mark.negative
def test_search_rejects_malformed_json(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        data="{not-json",
        headers={"Content-Type": "application/json"},
        timeout=3,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid JSON body"


@pytest.mark.negative
@pytest.mark.known_bug
def test_search_rejects_empty_query(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": ""},
        timeout=3,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "query cannot be empty"


@pytest.mark.negative
@pytest.mark.known_bug
def test_search_rejects_blank_query(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "   "},
        timeout=3,
    )

    assert response.status_code == 400
    assert response.json()["error"] == "query cannot be empty"
