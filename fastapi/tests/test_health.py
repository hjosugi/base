from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok", "env": "test"}


def test_request_id_is_returned(client: TestClient) -> None:
    res = client.get("/health")

    assert res.headers["X-Request-ID"]
    assert float(res.headers["X-Process-Time-Ms"]) >= 0


def test_request_id_from_client_is_reused(client: TestClient) -> None:
    res = client.get("/health", headers={"X-Request-ID": "abc123"})

    assert res.headers["X-Request-ID"] == "abc123"
