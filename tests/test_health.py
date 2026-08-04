from datetime import datetime, timezone


def test_health_returns_operational_metadata(api):
    response = api.health()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"
    assert body["services"] == 11

    timestamp = datetime.fromisoformat(body["timestamp"].replace("Z", "+00:00"))
    assert timestamp.tzinfo is not None
    assert timestamp <= datetime.now(timezone.utc)
