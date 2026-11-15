"""Logging setup with a request ID in every log line."""

import logging
import logging.config
from contextvars import ContextVar

# The middleware sets this for each request.
# Code inside the request can read it, even in a threadpool.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Add request_id to each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logging(level: str) -> None:
    """Configure the "todo_api" logger.

    We do not touch the uvicorn loggers. Uvicorn sets them up itself.
    """
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_id": {"()": RequestIdFilter},
            },
            "formatters": {
                "default": {
                    "format": (
                        "%(asctime)s %(levelname)-7s [%(request_id)s] "
                        "%(name)s: %(message)s"
                    ),
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["request_id"],
                },
            },
            "loggers": {
                "todo_api": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
            },
        }
    )
