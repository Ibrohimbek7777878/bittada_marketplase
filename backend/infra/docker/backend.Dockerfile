# Bittada backend image. Multi-stage to keep the runtime layer small.
FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps required at runtime by psycopg, Pillow, weasyprint, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq5 \
        libjpeg62-turbo \
        zlib1g \
        libwebp7 \
        libffi8 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- Builder stage installs everything; runtime copies only what is needed.
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
        libwebp-dev \
        libffi-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements/ /tmp/req/
ARG ENV=dev
RUN pip install -r /tmp/req/${ENV}.txt

# ---- Final image
FROM base AS final
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY backend /app

# Drop privileges.
RUN useradd --system --create-home --uid 1000 bittada \
    && chown -R bittada:bittada /app
USER bittada

EXPOSE 8000 8001

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/healthz || exit 1
