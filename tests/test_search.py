import pytest

from tests.data import (
    BENEFITS_CATEGORY,
    BENEFITS_SERVICE_IDS,
    BUS_PASS_SERVICE_ID,
    BUS_QUERY,
    HEALTH_QUERY,
    HEALTH_QUERY_UPPER,
    HEALTH_SERVICE_IDS,
    NO_MATCH_QUERY,
    SPACED_HEALTH_QUERY,
    VACCINATION_QUERY_WITHOUT_ACCENT,
    VACCINATION_SERVICE_ID,
)


@pytest.mark.contract
def test_search_finds_services_by_text_case_insensitive(api):
    response = api.search(HEALTH_QUERY_UPPER)

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == HEALTH_QUERY_UPPER
    assert body["total"] >= 2
    assert {item["id"] for item in body["results"]} >= HEALTH_SERVICE_IDS


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_returns_empty_result_set_when_no_service_matches(api):
    response = api.search(NO_MATCH_QUERY)

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == NO_MATCH_QUERY
    assert body["total"] == 0
    assert body["results"] == []


@pytest.mark.contract
def test_search_matches_category(api):
    response = api.search(BENEFITS_CATEGORY)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["id"] for item in body["results"]} == BENEFITS_SERVICE_IDS


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_is_accent_insensitive_for_user_typed_text(api):
    response = api.search(VACCINATION_QUERY_WITHOUT_ACCENT)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(item["id"] == VACCINATION_SERVICE_ID for item in body["results"])


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_trims_surrounding_spaces(api):
    response = api.search(SPACED_HEALTH_QUERY)

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == HEALTH_QUERY
    assert body["total"] >= 2
    assert {item["id"] for item in body["results"]} >= HEALTH_SERVICE_IDS


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_matches_tags_for_common_user_terms(api):
    response = api.search(BUS_QUERY)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert any(item["id"] == BUS_PASS_SERVICE_ID for item in body["results"])


@pytest.mark.negative
def test_search_rejects_malformed_json(api):
    response = api.search_raw(
        data="{not-json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid JSON body"


@pytest.mark.negative
@pytest.mark.known_bug
def test_search_rejects_empty_query(api):
    response = api.search("")

    assert response.status_code == 400
    assert response.json()["error"] == "query cannot be empty"


@pytest.mark.negative
@pytest.mark.known_bug
def test_search_rejects_blank_query(api):
    response = api.search("   ")

    assert response.status_code == 400
    assert response.json()["error"] == "query cannot be empty"
