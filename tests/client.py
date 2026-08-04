import requests

DEFAULT_TIMEOUT = 3


class CatalogApiClient:
    def __init__(self, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def close(self):
        self.session.close()

    def request(self, method: str, path: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{path}", **kwargs)

    def health(self):
        return self.request("GET", "/health")

    def list_services(self, page=None, per_page=None):
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        return self.request("GET", "/api/v1/services", params=params)

    def list_services_raw(self, query_string: str):
        return self.request("GET", f"/api/v1/services?{query_string}")

    def get_service(self, service_id: str):
        return self.request("GET", f"/api/v1/services/{service_id}")

    def search(self, query: str):
        return self.request("POST", "/api/v1/services/search", json={"query": query})

    def search_raw(self, **kwargs):
        return self.request("POST", "/api/v1/services/search", **kwargs)

    def recommendations(self, service_id: str, headers=None):
        return self.request(
            "GET",
            f"/api/v1/services/{service_id}/recommendations",
            headers=headers,
        )

    def favorite(self, service_id: str, headers=None):
        return self.request("POST", f"/api/v1/services/{service_id}/favorite", headers=headers)

    def webhook(self, **kwargs):
        return self.request("POST", "/api/v1/webhooks/catalog", **kwargs)

    def unsupported_services_put(self, payload):
        return self.request("PUT", "/api/v1/services", json=payload)
