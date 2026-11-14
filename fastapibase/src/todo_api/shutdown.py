"""Run a callback as soon as the server gets a stop signal.

Why we need this:
  On Ctrl+C or reload, Uvicorn first waits for all open connections
  to close. Only after that it runs the lifespan shutdown.
  An SSE stream never closes by itself, so the server waits forever
  ("Waiting for connections to close").

  So we hook the signal and end the streams early.
  Then Uvicorn can finish the normal shutdown.
"""

import asyncio
import logging
import signal
import threading
from collections.abc import Callable
from types import FrameType

logger = logging.getLogger(__name__)

# What signal.getsignal() can return (except None).
SignalHandler = Callable[[int, FrameType | None], object] | int | signal.Handlers

# The same signals that Uvicorn handles.
_SIGNALS = [signal.SIGINT, signal.SIGTERM]
if hasattr(signal, "SIGBREAK"):  # Windows only
    _SIGNALS.append(signal.SIGBREAK)


def on_shutdown_signal(callback: Callable[[], None]) -> Callable[[], None]:
    """Call `callback` in the event loop when a stop signal arrives.

    The original handler (Uvicorn's) still runs after ours.
    Returns a function that removes the hook.
    Call this from inside the running event loop (for example, the lifespan).
    """
    # Python allows signal handlers only in the main thread.
    # TestClient runs the app in another thread, so we skip it there.
    if threading.current_thread() is not threading.main_thread():
        return lambda: None

    loop = asyncio.get_running_loop()
    originals: dict[int, SignalHandler] = {}

    def handler(signum: int, frame: FrameType | None) -> None:
        logger.info("got signal %s: closing streams", signal.Signals(signum).name)
        # A signal handler must do very little.
        # We only schedule the callback in the event loop.
        loop.call_soon_threadsafe(callback)
        original = originals[signum]
        if callable(original):
            original(signum, frame)

    for sig in _SIGNALS:
        current = signal.getsignal(sig)
        if current is not None:
            originals[sig] = current
            signal.signal(sig, handler)

    def restore() -> None:
        for sig, original in originals.items():
            signal.signal(sig, original)

    return restore
