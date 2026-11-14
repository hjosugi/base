"""In-process event broker for WebSocket and SSE.

The Todo endpoints publish events here.
WebSocket and SSE clients subscribe and receive them.

This works only inside one process.
With many workers or many servers, use Redis Pub/Sub or similar.
"""

import asyncio
import contextlib
import logging
import threading
from collections import deque
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Literal, Self

from pydantic import BaseModel

from todo_api.schemas import Todo

logger = logging.getLogger(__name__)

EventType = Literal["created", "updated", "deleted"]


class TodoEvent(BaseModel):
    """One change to a Todo item."""

    id: int  # Sequence number. SSE uses it for Last-Event-ID.
    type: EventType
    todo_id: int
    todo: Todo | None = None  # None for "deleted"


class Subscription:
    """One subscriber. Read events with `async for`."""

    def __init__(self, loop: asyncio.AbstractEventLoop, maxsize: int) -> None:
        self._loop = loop
        # None is the "stream is closed" signal.
        self._queue: asyncio.Queue[TodoEvent | None] = asyncio.Queue(maxsize)

    def push(self, event: TodoEvent | None) -> None:
        """Send an event to this subscriber. Safe to call from any thread."""
        # RuntimeError means the loop is closed. The subscriber is gone.
        with contextlib.suppress(RuntimeError):
            self._loop.call_soon_threadsafe(self._offer, event)

    def _offer(self, event: TodoEvent | None) -> None:
        # This runs in the subscriber's event loop.
        if self._queue.full():
            # Slow client: drop the oldest event, keep the newest.
            dropped = self._queue.get_nowait()
            logger.warning("slow subscriber: dropped %s", dropped)
        self._queue.put_nowait(event)

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> TodoEvent:
        event = await self._queue.get()
        if event is None:
            raise StopAsyncIteration
        return event


class EventBroker:
    """Publish / subscribe for Todo events.

    `publish` can be called from sync endpoints (threadpool)
    and from async code. It is thread-safe.
    """

    def __init__(self, history_size: int = 100, queue_size: int = 100) -> None:
        self._lock = threading.Lock()
        self._subscribers: set[Subscription] = set()
        # Recent events, so a client can resume with Last-Event-ID.
        self._history: deque[TodoEvent] = deque(maxlen=history_size)
        self._next_id = 1
        self._queue_size = queue_size

    @property
    def subscriber_count(self) -> int:
        with self._lock:
            return len(self._subscribers)

    def publish(
        self, event_type: EventType, todo_id: int, todo: Todo | None = None
    ) -> TodoEvent:
        with self._lock:
            event = TodoEvent(
                id=self._next_id, type=event_type, todo_id=todo_id, todo=todo
            )
            self._next_id += 1
            self._history.append(event)
            # Push inside the lock, so every subscriber gets the same order.
            for sub in self._subscribers:
                sub.push(event)
        logger.debug("published %s", event)
        return event

    @asynccontextmanager
    async def subscribe(
        self, last_event_id: int | None = None
    ) -> AsyncGenerator[Subscription]:
        """Subscribe for the duration of the `async with` block.

        If last_event_id is given, first replay newer events from history.
        """
        sub = Subscription(asyncio.get_running_loop(), self._queue_size)
        with self._lock:
            if last_event_id is not None:
                for event in self._history:
                    if event.id > last_event_id:
                        sub.push(event)
            self._subscribers.add(sub)
            count = len(self._subscribers)
        logger.info("subscribed (subscribers=%d)", count)
        try:
            yield sub
        finally:
            # Runs on normal end, on client disconnect, and on cancel.
            with self._lock:
                self._subscribers.discard(sub)
                count = len(self._subscribers)
            logger.info("unsubscribed (subscribers=%d)", count)

    def close(self) -> None:
        """End all subscriptions. Call this on shutdown."""
        with self._lock:
            for sub in self._subscribers:
                sub.push(None)
