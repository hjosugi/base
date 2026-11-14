"""Unit tests for EventBroker (no HTTP)."""

import pytest

from todo_api.events import EventBroker, Subscription, TodoEvent

# The broker uses asyncio, so we run these tests on asyncio only.
pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def take(sub: Subscription, n: int) -> list[TodoEvent]:
    return [await anext(sub) for _ in range(n)]


async def test_subscriber_gets_events_in_order() -> None:
    broker = EventBroker()
    async with broker.subscribe() as sub:
        broker.publish("created", 1)
        broker.publish("updated", 1)
        broker.publish("deleted", 1)

        events = await take(sub, 3)

    assert [(e.id, e.type) for e in events] == [
        (1, "created"),
        (2, "updated"),
        (3, "deleted"),
    ]


async def test_replay_after_last_event_id() -> None:
    broker = EventBroker()
    for i in range(1, 4):
        broker.publish("created", i)

    async with broker.subscribe(last_event_id=1) as sub:
        events = await take(sub, 2)

    assert [e.id for e in events] == [2, 3]


async def test_unsubscribe_on_exit() -> None:
    broker = EventBroker()
    async with broker.subscribe():
        assert broker.subscriber_count == 1

    assert broker.subscriber_count == 0


async def test_close_ends_iteration() -> None:
    broker = EventBroker()
    async with broker.subscribe() as sub:
        broker.publish("created", 1)
        broker.close()

        received = [e.id async for e in sub]

    assert received == [1]


async def test_slow_subscriber_keeps_newest() -> None:
    broker = EventBroker(queue_size=2)
    async with broker.subscribe() as sub:
        for i in range(1, 5):
            broker.publish("created", i)

        events = await take(sub, 2)

    assert [e.id for e in events] == [3, 4]
