"""Shared pytest fixtures."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from todo_api.config import Settings
from todo_api.main import create_app


@pytest.fixture
def settings() -> Settings:
    """Settings for tests. We do not read .env here."""
    return Settings(_env_file=None, env="test", debug=False, log_level="DEBUG")


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    """A fresh app for each test, so tests do not share data."""
    return create_app(settings)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    """HTTP client for the app.

    The `with` block runs the lifespan (startup and shutdown).
    """
    with TestClient(app) as c:
        yield c
