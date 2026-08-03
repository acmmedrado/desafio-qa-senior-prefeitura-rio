import os
import time

import pytest
import requests


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
    return {"Authorization": f"Bearer {DEFAULT_TOKEN}"}


@pytest.fixture
def api(base_url):
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    session.base_url = base_url
    return session
