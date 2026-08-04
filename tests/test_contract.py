import re
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from tests.data import (
    FAVORITE_SERVICE_ID,
    HEALTH_QUERY,
    NO_MATCH_QUERY,
    VACCINATION_SERVICE_ID,
)

ROOT_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def openapi_spec():
    with (ROOT_DIR / "openapi.yaml").open(encoding="utf-8") as spec_file:
        return yaml.safe_load(spec_file)


def resolve_ref(spec, ref):
    node = spec
    for part in ref.removeprefix("#/").split("/"):
        node = node[part]
    return node


def schema_for(spec, path, method, status_code):
    schema = spec["paths"][path][method]["responses"][str(status_code)]["content"][
        "application/json"
    ]["schema"]
    if "$ref" in schema:
        return resolve_ref(spec, schema["$ref"])
    return schema


def inline_refs(spec, schema):
    if isinstance(schema, dict):
        if "$ref" in schema:
            return inline_refs(spec, resolve_ref(spec, schema["$ref"]))
        return {key: inline_refs(spec, value) for key, value in schema.items()}
    if isinstance(schema, list):
        return [inline_refs(spec, item) for item in schema]
    return schema


def validate_response(spec, path, method, status_code, payload):
    schema = schema_for(spec, path, method, status_code)
    schema = inline_refs(spec, schema)
    Draft202012Validator(schema).validate(payload)


@pytest.mark.contract
def test_health_matches_openapi_contract(api, openapi_spec):
    response = api.health()

    assert response.status_code == 200
    validate_response(openapi_spec, "/health", "get", 200, response.json())


@pytest.mark.contract
def test_services_list_matches_openapi_contract(api, openapi_spec):
    response = api.list_services(page=2, per_page=10)

    assert response.status_code == 200
    validate_response(openapi_spec, "/api/v1/services", "get", 200, response.json())


@pytest.mark.contract
def test_service_detail_matches_openapi_contract(api, openapi_spec):
    response = api.get_service(VACCINATION_SERVICE_ID)

    assert response.status_code == 200
    validate_response(openapi_spec, "/api/v1/services/{id}", "get", 200, response.json())


@pytest.mark.contract
def test_search_response_matches_openapi_contract(api, openapi_spec):
    response = api.search(HEALTH_QUERY)

    assert response.status_code == 200
    validate_response(openapi_spec, "/api/v1/services/search", "post", 200, response.json())


@pytest.mark.contract
def test_favorite_response_matches_openapi_contract(api, auth_headers, openapi_spec):
    response = api.favorite(
        FAVORITE_SERVICE_ID,
        headers=auth_headers,
    )

    assert response.status_code == 200
    validate_response(openapi_spec, "/api/v1/services/{id}/favorite", "post", 200, response.json())


@pytest.mark.contract
def test_recommendations_response_matches_openapi_contract(api, auth_headers, openapi_spec):
    response = api.recommendations(
        VACCINATION_SERVICE_ID,
        headers=auth_headers,
    )

    assert response.status_code == 200
    validate_response(
        openapi_spec,
        "/api/v1/services/{id}/recommendations",
        "get",
        200,
        response.json(),
    )


@pytest.mark.contract
def test_all_service_ids_follow_public_contract(api):
    response = api.list_services(per_page=100)

    assert response.status_code == 200
    assert all(re.fullmatch(r"s\d{3}", service["id"]) for service in response.json()["data"])


@pytest.mark.contract
def test_all_services_have_non_negative_view_count(api):
    response = api.list_services(per_page=100)

    assert response.status_code == 200
    assert all(service["view_count"] >= 0 for service in response.json()["data"])


@pytest.mark.contract
def test_all_services_have_non_empty_string_tags(api):
    response = api.list_services(per_page=100)

    assert response.status_code == 200
    assert all(
        service["tags"] and all(isinstance(tag, str) and tag.strip() for tag in service["tags"])
        for service in response.json()["data"]
    )


@pytest.mark.contract
def test_service_detail_is_consistent_with_list_response(api):
    list_response = api.list_services(per_page=100)
    list_response.raise_for_status()

    for listed_service in list_response.json()["data"]:
        detail_response = api.get_service(listed_service["id"])
        assert detail_response.status_code == 200
        assert detail_response.json() == listed_service


@pytest.mark.contract
def test_recommendations_reference_existing_services_and_do_not_self_reference(api, auth_headers):
    service_response = api.list_services(per_page=100)
    service_response.raise_for_status()
    existing_ids = {service["id"] for service in service_response.json()["data"]}

    response = api.recommendations(VACCINATION_SERVICE_ID, headers=auth_headers)

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert all(item["id"] in existing_ids for item in recommendations)
    assert all(item["id"] != VACCINATION_SERVICE_ID for item in recommendations)


@pytest.mark.contract
@pytest.mark.known_bug
def test_empty_search_response_matches_openapi_contract(api, openapi_spec):
    response = api.search(NO_MATCH_QUERY)

    assert response.status_code == 200
    validate_response(openapi_spec, "/api/v1/services/search", "post", 200, response.json())
