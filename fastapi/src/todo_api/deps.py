"""Dependencies for path operations (FastAPI Depends)."""

from typing import Annotated, cast

from fastapi import Depends
from fastapi.requests import HTTPConnection

from todo_api.config import Settings
from todo_api.events import EventBroker
from todo_api.repository import TodoRepository

# We use HTTPConnection, not Request.
# HTTPConnection is the base class of both Request and WebSocket,
# so these dependencies also work in WebSocket endpoints.


def get_repository(conn: HTTPConnection) -> TodoRepository:
    """Return the repository that the lifespan put on app.state."""
    return cast(TodoRepository, conn.app.state.todo_repo)


def get_broker(conn: HTTPConnection) -> EventBroker:
    """Return the event broker that the lifespan put on app.state."""
    return cast(EventBroker, conn.app.state.event_broker)


def get_app_settings(conn: HTTPConnection) -> Settings:
    """Return the Settings object used to build this app."""
    return cast(Settings, conn.app.state.settings)


# Use these type aliases in path operations.
# Ruff rule FAST002 asks for this Annotated style.
RepoDep = Annotated[TodoRepository, Depends(get_repository)]
BrokerDep = Annotated[EventBroker, Depends(get_broker)]
SettingsDep = Annotated[Settings, Depends(get_app_settings)]
