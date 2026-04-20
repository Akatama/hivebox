FROM python:3.14-slim AS base

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1

FROM base AS build

COPY --from=ghcr.io/astral-sh/uv:0.9.11 /uv /bin/uv

# UV_COMPILE_BYTECODE=1 is an important startup time optimization
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /project

COPY uv.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

FROM base AS runtime

RUN addgroup --gid 1001 --system nonroot && \
  adduser --no-create-home --shell /bin/false \
  --disabled-password --uid 1001 --system --group nonroot

USER nonroot:nonroot

WORKDIR /project

ENV VIRTUAL_ENV=/app/.venv \
  PATH="/project/.venv/bin:$PATH"

COPY --from=build --chown=nonroot:nonroot /project ./

EXPOSE 8000

CMD [ "fastapi", "run", "./app/main.py"]
