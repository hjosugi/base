"""HTTP middleware: request ID and access log with timing."""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from todo_api.log_config import request_id_var

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


async def request_context(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Set a request ID, call the app, then log the result."""
    # Reuse the client's ID if it sends one. Otherwise make a new one.
    request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:12]
    token = request_id_var.set(request_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
        logger.info(
            "%s %s -> %d (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response
    finally:
        # Always reset, so the ID does not leak to the next request.
        request_id_var.reset(token)
