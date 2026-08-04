import pytest


@pytest.mark.contract
def test_service_content_supports_public_service_comprehension(api):
    response = api.get(f"{api.base_url}/api/v1/services?per_page=100", timeout=3)

    assert response.status_code == 200
    services = response.json()["data"]
    assert services

    for service in services:
        assert service["title"].strip()
        assert len(service["description"].strip()) >= 40
        assert service["category"].strip()
        assert service["organization"].strip()
        assert len(service["tags"]) >= 3
        assert service["active"] is True


@pytest.mark.contract
def test_service_categories_are_machine_stable_and_frontend_friendly(api):
    response = api.get(f"{api.base_url}/api/v1/services?per_page=100", timeout=3)

    assert response.status_code == 200
    categories = {service["category"] for service in response.json()["data"]}

    assert categories == {
        "assistencia_social",
        "beneficios",
        "educacao",
        "empresas",
        "habitacao",
        "meio_ambiente",
        "saude",
        "trabalho",
        "transporte",
    }
    assert all(category == category.lower() for category in categories)
    assert all(" " not in category for category in categories)


@pytest.mark.contract
def test_user_can_complete_search_to_detail_to_recommendation_journey(api, auth_headers):
    search_response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "vacina"},
        timeout=3,
    )
    assert search_response.status_code == 200

    results = search_response.json()["results"]
    assert results
    selected = next(item for item in results if item["id"] == "s002")

    detail_response = api.get(
        f"{api.base_url}/api/v1/services/{selected['id']}",
        timeout=3,
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == selected["title"]

    recommendations_response = api.get(
        f"{api.base_url}/api/v1/services/{selected['id']}/recommendations",
        headers=auth_headers,
        timeout=3,
    )
    assert recommendations_response.status_code == 200
    recommendations = recommendations_response.json()["recommendations"]
    assert recommendations
    assert all(item["category"] == selected["category"] for item in recommendations)


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_prioritizes_title_matches_over_description_matches(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "familia"},
        timeout=3,
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results is not None
    assert results[0]["id"] == "s011"


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_supports_need_based_language_for_school_enrollment(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "matricular filho"},
        timeout=3,
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results is not None
    assert any(item["id"] == "s003" for item in results)


@pytest.mark.contract
@pytest.mark.known_bug
def test_search_supports_need_based_language_for_opening_a_business(api):
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": "abrir comercio"},
        timeout=3,
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results is not None
    assert any(item["id"] == "s009" for item in results)
