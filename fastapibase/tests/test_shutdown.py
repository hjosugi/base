"""Tests for the shutdown signal hook."""

import asyncio
import signal
import threading
from types import FrameType

import pytest

from todo_api.shutdown import on_shutdown_signal

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_signal_runs_callback_and_original_handler() -> None:
    calls: list[str] = []

    def original(signum: int, frame: FrameType | None) -> None:
        calls.append("original")

    saved = signal.signal(signal.SIGTERM, original)
    try:
        remove = on_shutdown_signal(lambda: calls.append("callback"))
        signal.raise_signal(signal.SIGTERM)
        # The callback runs in the event loop, so give it a moment.
        await asyncio.sleep(0.05)
        remove()
        restored = signal.getsignal(signal.SIGTERM)
    finally:
        signal.signal(signal.SIGTERM, saved)

    # The original handler runs at once. The callback runs a bit later.
    assert calls == ["original", "callback"]
    assert restored is original


def test_no_hook_outside_main_thread() -> None:
    result: list[object] = []

    def worker() -> None:
        remove = on_shutdown_signal(lambda: None)
        remove()  # must be a safe no-op
        result.append(remove)

    t = threading.Thread(target=worker)
    t.start()
    t.join()

    assert len(result) == 1
