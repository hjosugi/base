"""Request and response models (Pydantic)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoCreate(BaseModel):
    """Body for POST /todos."""

    # Reject unknown fields. This finds typos in the client early.
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=100, examples=["Buy milk"])
    done: bool = False


class TodoUpdate(BaseModel):
    """Body for PATCH /todos/{todo_id}. All fields are optional."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None


class Todo(BaseModel):
    """A Todo item returned by the API."""

    id: int
    title: str
    done: bool
    created_at: datetime


class TodoStats(BaseModel):
    """Summary of all Todo items."""

    total: int
    done: int
    done_ratio: float
