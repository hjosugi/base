from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from todo_api.deps import get_repository
from todo_api.repository import TodoRepository
from todo_api.schemas import Todo, TodoCreate, TodoUpdate


def create(client: TestClient, title: str, *, done: bool = False) -> int:
    """Create a Todo item and return its ID."""
    res = client.post("/todos", json={"title": title, "done": done})
    assert res.status_code == 201
    todo_id: int = res.json()["id"]
    return todo_id


def test_create_and_get(client: TestClient) -> None:
    todo_id = create(client, "Buy milk")

    res = client.get(f"/todos/{todo_id}")

    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "Buy milk"
    assert body["done"] is False


def test_list_with_filter_and_paging(client: TestClient) -> None:
    create(client, "a", done=True)
    create(client, "b")
    create(client, "c", done=True)

    done_items = client.get("/todos", params={"done": True}).json()
    page = client.get("/todos", params={"limit": 1, "offset": 1}).json()

    assert [t["title"] for t in done_items] == ["a", "c"]
    assert [t["title"] for t in page] == ["b"]


@pytest.mark.parametrize(
    "body",
    [
        {"title": ""},  # too short
        {"title": "x" * 101},  # too long
        {"done": True},  # title is missing
        {"title": "ok", "unknown": 1},  # extra field
    ],
)
def test_create_validation_error(client: TestClient, body: dict[str, object]) -> None:
    res = client.post("/todos", json=body)

    assert res.status_code == 422


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
def test_list_query_validation_error(
    client: TestClient, params: dict[str, int]
) -> None:
    res = client.get("/todos", params=params)

    assert res.status_code == 422


def test_get_not_found(client: TestClient) -> None:
    res = client.get("/todos/999")

    assert res.status_code == 404
    assert res.json() == {"detail": "Todo 999 not found"}


def test_path_param_must_be_int(client: TestClient) -> None:
    res = client.get("/todos/abc")

    assert res.status_code == 422


def test_update_only_sent_fields(client: TestClient) -> None:
    todo_id = create(client, "Read a book")

    res = client.patch(f"/todos/{todo_id}", json={"done": True})

    assert res.status_code == 200
    assert res.json()["title"] == "Read a book"
    assert res.json()["done"] is True


def test_update_not_found(client: TestClient) -> None:
    res = client.patch("/todos/999", json={"done": True})

    assert res.status_code == 404


def test_delete(client: TestClient) -> None:
    todo_id = create(client, "Temp")

    first = client.delete(f"/todos/{todo_id}")
    second = client.delete(f"/todos/{todo_id}")

    assert first.status_code == 204
    assert second.status_code == 404


def test_stats_when_empty(client: TestClient) -> None:
    res = client.get("/todos/stats")

    assert res.status_code == 200
    assert res.json() == {"total": 0, "done": 0, "done_ratio": 0.0}


def test_stats(client: TestClient) -> None:
    create(client, "a", done=True)
    create(client, "b")

    res = client.get("/todos/stats")

    assert res.json() == {"total": 2, "done": 1, "done_ratio": 0.5}


class FakeRepo:
    """A fake repository with one fixed item."""

    def __init__(self) -> None:
        self.item = Todo(
            id=42,
            title="from fake",
            done=False,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    def list_items(self, *, done: bool | None, limit: int, offset: int) -> list[Todo]:
        return [self.item]

    def get(self, todo_id: int) -> Todo | None:
        return self.item if todo_id == self.item.id else None

    def add(self, data: TodoCreate) -> Todo:
        raise NotImplementedError

    def update(self, todo_id: int, data: TodoUpdate) -> Todo | None:
        raise NotImplementedError

    def delete(self, todo_id: int) -> bool:
        raise NotImplementedError


def test_dependency_override(app: FastAPI, client: TestClient) -> None:
    # Replace the real repository with a fake one.
    # mypy checks that FakeRepo matches the TodoRepository Protocol.
    fake: TodoRepository = FakeRepo()
    app.dependency_overrides[get_repository] = lambda: fake

    res = client.get("/todos/42")

    assert res.status_code == 200
    assert res.json()["title"] == "from fake"
