"""Tests for the WebSocket endpoint /ws/todos."""

import time

import pytest
from fastapi import FastAPI, WebSocketDisconnect
from fastapi.testclient import TestClient


def wait_until_subscribed(app: FastAPI, count: int = 1) -> None:
    """The endpoint subscribes after accept(). Wait for it."""
    broker = app.state.event_broker
    deadline = time.monotonic() + 2
    while broker.subscriber_count != count:
        assert time.monotonic() < deadline, "timeout"
        time.sleep(0.01)


def test_ping_pong(client: TestClient) -> None:
    with client.websocket_connect("/ws/todos") as ws:
        ws.send_json({"type": "ping"})

        assert ws.receive_json() == {"type": "pong"}


def test_create_via_websocket(client: TestClient) -> None:
    with client.websocket_connect("/ws/todos") as ws:
        ws.send_json({"type": "create", "title": "from ws"})
        msg = ws.receive_json()

    assert msg["type"] == "event"
    assert msg["data"]["type"] == "created"
    assert msg["data"]["todo"]["title"] == "from ws"
    # The item is also visible over HTTP.
    assert client.get("/todos/1").json()["title"] == "from ws"


def test_http_change_is_pushed_to_websocket(app: FastAPI, client: TestClient) -> None:
    with client.websocket_connect("/ws/todos") as ws:
        wait_until_subscribed(app)
        client.post("/todos", json={"title": "from http"})

        msg = ws.receive_json()

    assert msg["data"]["todo"]["title"] == "from http"


@pytest.mark.parametrize(
    ("text", "error_type"),
    [
        ('{"type": "create", "title": ""}', "string_too_short"),
        ('{"type": "unknown"}', "union_tag_invalid"),
        ("not json", "json_invalid"),
    ],
)
def test_invalid_message_returns_error(
    client: TestClient, text: str, error_type: str
) -> None:
    with client.websocket_connect("/ws/todos") as ws:
        ws.send_text(text)
        msg = ws.receive_json()
        # The connection is still open after an error.
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()

    assert msg["type"] == "error"
    assert msg["errors"][0]["type"] == error_type
    assert pong == {"type": "pong"}


def test_unsubscribe_on_disconnect(app: FastAPI, client: TestClient) -> None:
    with client.websocket_connect("/ws/todos"):
        wait_until_subscribed(app, 1)

    wait_until_subscribed(app, 0)


def test_server_shutdown_closes_socket(app: FastAPI, client: TestClient) -> None:
    with client.websocket_connect("/ws/todos") as ws:
        wait_until_subscribed(app)
        app.state.event_broker.close()

        with pytest.raises(WebSocketDisconnect) as exc_info:
            ws.receive_json()

    assert exc_info.value.code == 1001


def test_demo_page(client: TestClient) -> None:
    res = client.get("/demo")

    assert res.status_code == 200
    assert "EventSource" in res.text
    assert "WebSocket" in res.text
