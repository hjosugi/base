"""Storage for Todo items.

We define an interface (Protocol) and one in-memory implementation.
Later you can add a database implementation with the same interface.
"""

import threading
from datetime import UTC, datetime
from typing import Protocol

from todo_api.schemas import Todo, TodoCreate, TodoUpdate


class TodoRepository(Protocol):
    """Interface for Todo storage."""

    def list_items(
        self, *, done: bool | None, limit: int, offset: int
    ) -> list[Todo]: ...

    def get(self, todo_id: int) -> Todo | None: ...

    def add(self, data: TodoCreate) -> Todo: ...

    def update(self, todo_id: int, data: TodoUpdate) -> Todo | None: ...

    def delete(self, todo_id: int) -> bool: ...


class InMemoryTodoRepository:
    """Keep Todo items in a dict. Data is lost on restart."""

    def __init__(self) -> None:
        self._items: dict[int, Todo] = {}
        self._next_id = 1
        # Sync endpoints run in a threadpool, so we use a lock.
        self._lock = threading.Lock()

    def list_items(self, *, done: bool | None, limit: int, offset: int) -> list[Todo]:
        items = sorted(self._items.values(), key=lambda t: t.id)
        if done is not None:
            items = [t for t in items if t.done is done]
        return items[offset : offset + limit]

    def get(self, todo_id: int) -> Todo | None:
        return self._items.get(todo_id)

    def add(self, data: TodoCreate) -> Todo:
        with self._lock:
            todo = Todo(
                id=self._next_id,
                title=data.title,
                done=data.done,
                created_at=datetime.now(UTC),
            )
            self._items[todo.id] = todo
            self._next_id += 1
        return todo

    def update(self, todo_id: int, data: TodoUpdate) -> Todo | None:
        with self._lock:
            current = self._items.get(todo_id)
            if current is None:
                return None
            # exclude_unset=True: only change fields the client sent.
            changes = data.model_dump(exclude_unset=True)
            updated = current.model_copy(update=changes)
            self._items[todo_id] = updated
        return updated

    def delete(self, todo_id: int) -> bool:
        with self._lock:
            return self._items.pop(todo_id, None) is not None
