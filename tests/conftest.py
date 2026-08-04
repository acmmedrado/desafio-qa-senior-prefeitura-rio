import os
import time
from copy import deepcopy

import pytest
import requests

from tests.client import CatalogApiClient
from tests.data import UNKNOWN_SERVICE_ID

DEFAULT_TOKEN = "qa-challenge-token"


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", "http://localhost:8080").rstrip("/")


@pytest.fixture(scope="session", autouse=True)
def wait_for_api(base_url):
    deadline = time.time() + int(os.getenv("API_STARTUP_TIMEOUT", "30"))
    last_error = None

    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                return
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(1)

    raise RuntimeError(f"API did not become healthy at {base_url}: {last_error}")


@pytest.fixture
def auth_headers():
    token = os.getenv("AUTH_TOKEN", DEFAULT_TOKEN)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def api(base_url):
    client = CatalogApiClient(base_url)
    yield client
    client.close()


@pytest.fixture
def catalog_snapshot(api):
    response = api.list_services(per_page=100)
    response.raise_for_status()
    return deepcopy(response.json()["data"])


@pytest.fixture
def catalog(catalog_snapshot):
    class CatalogData:
        def __init__(self, services):
            self.services = services

        def by_id(self, service_id):
            return next(service for service in self.services if service["id"] == service_id)

        def by_title(self, title):
            return next(service for service in self.services if service["title"] == title)

        def by_category(self, category):
            return next(service for service in self.services if service["category"] == category)

        def by_tag(self, tag):
            return next(service for service in self.services if tag in service["tags"])

        def unknown_id(self):
            existing_ids = {service["id"] for service in self.services}
            candidate = UNKNOWN_SERVICE_ID
            assert candidate not in existing_ids
            return candidate

    return CatalogData(catalog_snapshot)
