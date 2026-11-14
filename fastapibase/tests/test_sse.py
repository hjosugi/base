"""Tests for the SSE endpoint GET /todos/events."""

import json
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

SseEvent = dict[str, str]


def read_event(lines: Iterator[str]) -> SseEvent:
    """Read lines until a blank line. Return the fields of one event.

    Comment lines (": ...") become {"comment": "..."}.
    """
    event: SseEvent = {}
    for line in lines:
        if line == "":
            if event:
                return event
            continue
        name, _, value = line.partition(":")
        key = name or "comment"
        event[key] = value.removeprefix(" ")
    raise AssertionError("stream ended")


@contextmanager
def open_stream(
    client: TestClient, headers: dict[str, str] | None = None
) -> Generator[Iterator[str]]:
    """Open the SSE stream and wait for the "connected" comment."""
    with client.stream("GET", "/todos/events", headers=headers) as res:
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/event-stream")
        lines = res.iter_lines()
        first = read_event(lines)
        assert first == {"comment": "connected", "retry": "3000"}
        yield lines
    # Leaving the block closes the connection.


def data_of(event: SseEvent) -> Any:
    return json.loads(event["data"])


def test_sse_receives_crud_events(client: TestClient) -> None:
    with open_stream(client) as lines:
        todo_id = client.post("/todos", json={"title": "a"}).json()["id"]
        client.patch(f"/todos/{todo_id}", json={"done": True})
        client.delete(f"/todos/{todo_id}")

        created = read_event(lines)
        updated = read_event(lines)
        deleted = read_event(lines)

    assert created["event"] == "created"
    assert created["id"] == "1"
    assert data_of(created)["todo"]["title"] == "a"
    assert updated["event"] == "updated"
    assert data_of(updated)["todo"]["done"] is True
    assert deleted["event"] == "deleted"
    assert data_of(deleted)["todo"] is None


def test_sse_resumes_from_last_event_id(client: TestClient) -> None:
    for title in ["a", "b", "c"]:
        client.post("/todos", json={"title": title})

    with open_stream(client, headers={"Last-Event-ID": "1"}) as lines:
        events = [read_event(lines), read_event(lines)]

    assert [e["id"] for e in events] == ["2", "3"]


def test_sse_bad_last_event_id(client: TestClient) -> None:
    res = client.get("/todos/events", headers={"Last-Event-ID": "abc"})

    assert res.status_code == 422


def test_sse_unsubscribes_on_disconnect(app: FastAPI, client: TestClient) -> None:
    broker = app.state.event_broker
    with open_stream(client):
        assert broker.subscriber_count == 1

    assert broker.subscriber_count == 0
