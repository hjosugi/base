"""A small browser page to try WebSocket and SSE."""

from importlib.resources import files

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(include_in_schema=False)

_DEMO_HTML = files("todo_api").joinpath("static/demo.html").read_text("utf-8")


@router.get("/demo", response_class=HTMLResponse)
def demo() -> str:
    """Return the demo page."""
    return _DEMO_HTML
