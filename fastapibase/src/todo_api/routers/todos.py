"""Todo CRUD endpoints."""

import logging
from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Query, Response, status
from fastapi.sse import EventSourceResponse, ServerSentEvent

from todo_api.deps import BrokerDep, RepoDep
from todo_api.schemas import Todo, TodoCreate, TodoStats, TodoUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/todos", tags=["todos"])


def _not_found(todo_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Todo {todo_id} not found",
    )


@router.get("")
def list_todos(
    repo: RepoDep,
    # Query parameters. FastAPI checks the type and the range.
    done: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Todo]:
    """List Todo items. Filter by `done` if you pass it."""
    return repo.list_items(done=done, limit=limit, offset=offset)


# Define /stats and /events before /{todo_id}.
# Routes match in order, and "stats" is not an int.
@router.get("/stats")
def todo_stats(repo: RepoDep) -> TodoStats:
    """Return the total count and the ratio of done items."""
    items = repo.list_items(done=None, limit=10_000, offset=0)
    total = len(items)
    done = sum(1 for t in items if t.done)
    # Guard against division by zero when there are no items.
    ratio = done / total if total else 0.0
    return TodoStats(total=total, done=done, done_ratio=ratio)


@router.get("/events", response_class=EventSourceResponse)
async def todo_events(
    broker: BrokerDep,
    # A browser sends this header when it reconnects.
    last_event_id: Annotated[int | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    """Stream Todo changes as Server-Sent Events (SSE)."""
    # Subscribe first, then say "connected".
    # So no event is lost between the two steps.
    async with broker.subscribe(last_event_id) as sub:
        # A comment line. Clients ignore it. retry: reconnect wait in ms.
        yield ServerSentEvent(comment="connected", retry=3000)
        async for event in sub:
            yield ServerSentEvent(data=event, event=event.type, id=str(event.id))


@router.get("/{todo_id}")
def get_todo(todo_id: int, repo: RepoDep) -> Todo:
    """Get one Todo item by ID."""
    todo = repo.get(todo_id)
    if todo is None:
        raise _not_found(todo_id)
    return todo


@router.post("", status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, repo: RepoDep, broker: BrokerDep) -> Todo:
    """Create a Todo item."""
    todo = repo.add(payload)
    logger.debug("created todo: %s", todo)
    broker.publish("created", todo.id, todo)
    return todo


@router.patch("/{todo_id}")
def update_todo(
    todo_id: int, payload: TodoUpdate, repo: RepoDep, broker: BrokerDep
) -> Todo:
    """Change some fields of a Todo item."""
    todo = repo.update(todo_id, payload)
    if todo is None:
        raise _not_found(todo_id)
    broker.publish("updated", todo.id, todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, repo: RepoDep, broker: BrokerDep) -> Response:
    """Delete a Todo item."""
    if not repo.delete(todo_id):
        raise _not_found(todo_id)
    broker.publish("deleted", todo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
