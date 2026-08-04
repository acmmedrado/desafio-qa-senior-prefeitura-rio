from concurrent.futures import ThreadPoolExecutor

import pytest

from tests.data import UNKNOWN_SERVICE_ID


@pytest.mark.contract
def test_health_handles_small_burst_of_concurrent_requests(api):
    def get_health():
        return api.health().status_code

    with ThreadPoolExecutor(max_workers=10) as executor:
        statuses = list(executor.map(lambda _: get_health(), range(50)))

    assert statuses == [200] * 50


@pytest.mark.contract
def test_health_handles_connection_close_requests(api):
    statuses = [
        api.request("GET", "/health", headers={"Connection": "close"}).status_code for _ in range(5)
    ]

    assert statuses == [200] * 5


@pytest.mark.negative
def test_unsupported_method_on_services_does_not_return_server_error(api):
    response = api.unsupported_services_put({"id": UNKNOWN_SERVICE_ID})

    assert response.status_code in {404, 405}


@pytest.mark.negative
def test_search_with_long_unicode_query_does_not_return_server_error(api):
    query = "ônibus grátis para idoso " * 200
    response = api.search(query)

    assert response.status_code < 500


@pytest.mark.negative
def test_webhook_large_unsigned_payload_does_not_return_server_error(api):
    response = api.webhook(
        json={"event": "bulk", "items": [{"id": f"s{i:03d}"} for i in range(1000)]},
    )

    assert response.status_code < 500
