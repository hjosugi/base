"""WebSocket endpoint: two-way messages + Todo events."""

import json
import logging
import uuid
from typing import Annotated, Literal

import anyio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from todo_api.deps import BrokerDep, RepoDep
from todo_api.events import EventBroker, Subscription
from todo_api.log_config import request_id_var
from todo_api.repository import TodoRepository
from todo_api.schemas import TodoCreate

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


# ---------------------------------------------------------------------------
# Messages from the client. "type" decides which model is used.
# ---------------------------------------------------------------------------
class PingMessage(BaseModel):
    type: Literal["ping"]


class CreateMessage(BaseModel):
    type: Literal["create"]
    title: str = Field(min_length=1, max_length=100)


ClientMessage = Annotated[PingMessage | CreateMessage, Field(discriminator="type")]
client_message_adapter: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)


@router.websocket("/ws/todos")
async def todo_ws(websocket: WebSocket, repo: RepoDep, broker: BrokerDep) -> None:
    """Send Todo events to the client, and handle client messages.

    Client -> server:
      {"type": "ping"}
      {"type": "create", "title": "..."}
    Server -> client:
      {"type": "pong"}
      {"type": "event", "data": {...TodoEvent...}}
      {"type": "error", "errors": [...]}
    """
    await websocket.accept()
    # HTTP middleware does not run for WebSocket, so we set the ID here.
    token = request_id_var.set(f"ws-{uuid.uuid4().hex[:8]}")
    logger.info("websocket connected")
    try:
        async with broker.subscribe() as sub, anyio.create_task_group() as tg:
            # Task 1: forward events from the broker to the client.
            tg.start_soon(_forward_events, websocket, sub)
            # Task 2 (this one): read messages from the client.
            await _receive_loop(websocket, repo, broker)
            # The client left. Stop task 1 too.
            tg.cancel_scope.cancel()
    finally:
        logger.info("websocket closed")
        request_id_var.reset(token)


async def _forward_events(websocket: WebSocket, sub: Subscription) -> None:
    try:
        async for event in sub:
            await websocket.send_json(
                {"type": "event", "data": event.model_dump(mode="json")}
            )
    except WebSocketDisconnect, RuntimeError:
        # The socket is already closed. Nothing to do.
        return
    # The broker closed the stream (server shutdown). Close the socket.
    await websocket.close(code=status.WS_1001_GOING_AWAY)


async def _receive_loop(
    websocket: WebSocket, repo: TodoRepository, broker: EventBroker
) -> None:
    while True:
        try:
            text = await websocket.receive_text()
        except WebSocketDisconnect as exc:
            logger.info("client disconnected (code=%s)", exc.code)
            return

        # Validate JSON and fields in one step.
        try:
            message = client_message_adapter.validate_json(text)
        except ValidationError as exc:
            errors = json.loads(exc.json(include_url=False))
            await websocket.send_json({"type": "error", "errors": errors})
            continue

        match message:
            case PingMessage():
                await websocket.send_json({"type": "pong"})
            case CreateMessage(title=title):
                todo = repo.add(TodoCreate(title=title))
                # Every subscriber gets this, including this client.
                broker.publish("created", todo.id, todo)
