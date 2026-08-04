from concurrent.futures import ThreadPoolExecutor

import pytest


@pytest.mark.contract
def test_health_handles_small_burst_of_concurrent_requests(api):
    def get_health():
        return api.get(f"{api.base_url}/health", timeout=3).status_code

    with ThreadPoolExecutor(max_workers=10) as executor:
        statuses = list(executor.map(lambda _: get_health(), range(20)))

    assert statuses == [200] * 20


@pytest.mark.negative
def test_unsupported_method_on_services_does_not_return_server_error(api):
    response = api.put(f"{api.base_url}/api/v1/services", json={"id": "s999"}, timeout=3)

    assert response.status_code in {404, 405}


@pytest.mark.negative
def test_search_with_long_unicode_query_does_not_return_server_error(api):
    query = "ônibus grátis para idoso " * 200
    response = api.post(
        f"{api.base_url}/api/v1/services/search",
        json={"query": query},
        timeout=3,
    )

    assert response.status_code < 500


@pytest.mark.negative
def test_webhook_large_unsigned_payload_does_not_return_server_error(api):
    response = api.post(
        f"{api.base_url}/api/v1/webhooks/catalog",
        json={"event": "bulk", "items": [{"id": f"s{i:03d}"} for i in range(1000)]},
        timeout=3,
    )

    assert response.status_code < 500
