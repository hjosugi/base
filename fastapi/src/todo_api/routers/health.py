"""Health check endpoint."""

from fastapi import APIRouter

from todo_api.deps import SettingsDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: SettingsDep) -> dict[str, str]:
    """Return "ok" when the app is running."""
    return {"status": "ok", "env": settings.env}
