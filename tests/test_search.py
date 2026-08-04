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


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_returns_empty_result_set_when_no_service_matches(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "termo-sem-correspondencia"},
        timeout=3,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "termo-sem-correspondencia"
    assert body["total"] == 0
    assert body["results"] == []


@pytest.mark.contract
def test_search_matches_category(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "beneficios"},
        timeout=3,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["id"] for item in body["results"]} == {"s001", "s011"}


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_is_accent_insensitive_for_user_typed_text(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "vacinacao"},
        timeout=3,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(item["id"] == "s002" for item in body["results"])


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_trims_surrounding_spaces(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "  saude  "},
        timeout=3,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "saude"
    assert body["total"] >= 2
    assert {item["id"] for item in body["results"]} >= {"s002", "s010"}


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_matches_tags_for_common_user_terms(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "onibus"},
        timeout=3,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(item["id"] == "s006" for item in body["results"])


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
