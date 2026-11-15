FROM ghcr.io/astral-sh/uv:0.13.8 AS uv
FROM python:3.15.2-slim

COPY --from=uv /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock .python-version README.md ./
COPY src ./src
COPY tests ./tests
RUN uv sync --locked && uv run pytest -q

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["wordcount"]
CMD ["README.md", "-n", "5"]
