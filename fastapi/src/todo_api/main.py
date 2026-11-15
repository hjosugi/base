"""App factory and the `app` object for the FastAPI CLI."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from todo_api.config import Settings, get_settings
from todo_api.events import EventBroker
from todo_api.log_config import setup_logging
from todo_api.middleware import request_context
from todo_api.repository import InMemoryTodoRepository
from todo_api.routers import demo, health, todos, ws
from todo_api.shutdown import on_shutdown_signal

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build a new app.

    Tests call this to get a fresh app for each test.
    """
    settings = settings or get_settings()
    setup_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        # Startup: create shared objects.
        app.state.todo_repo = InMemoryTodoRepository()
        app.state.event_broker = broker = EventBroker()
        # On Ctrl+C or reload, end SSE / WebSocket streams at once.
        # See shutdown.py for why.
        remove_hook = on_shutdown_signal(broker.close)
        logger.info("startup: env=%s debug=%s", settings.env, settings.debug)
        yield
        # Shutdown: end any streams that are still open.
        remove_hook()
        broker.close()
        logger.info("shutdown")

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.middleware("http")(request_context)
    app.include_router(health.router)
    app.include_router(todos.router)
    app.include_router(ws.router)
    app.include_router(demo.router)
    return app


app = create_app()


if __name__ == "__main__":
    # Run with: uv run python -m todo_api.main
    # This is handy for any debugger, because there is no reload process.
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
