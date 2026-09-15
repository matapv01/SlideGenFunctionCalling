# ── Stage 1: Build frontend ──────────────────────────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /app

# Install dependencies (copy lockfile first for layer caching)
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci --legacy-peer-deps

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build production bundle
COPY frontend/ ./frontend/
RUN cd frontend && npm run build


# ── Stage 2: Build Python dependencies ──────────────────────────────────────
FROM python:3.11-slim AS python-deps

WORKDIR /app

# Install uv binary (no pip)
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

# Network hardening for unstable links to package indexes.
ARG UV_HTTP_TIMEOUT=180
ARG UV_HTTP_CONNECT_TIMEOUT=30
ARG UV_HTTP_RETRIES=8

ENV UV_HTTP_TIMEOUT=${UV_HTTP_TIMEOUT} \
    UV_HTTP_CONNECT_TIMEOUT=${UV_HTTP_CONNECT_TIMEOUT} \
    UV_HTTP_RETRIES=${UV_HTTP_RETRIES}

# Install Python deps into a virtualenv (lockfile ensures reproducibility)
COPY pyproject.toml uv.lock ./
RUN sh -c 'for i in 1 2 3; do \
        echo "[BUILD] uv sync attempt $i/3"; \
        uv sync --frozen --no-dev && exit 0; \
        echo "[BUILD] uv sync failed, retrying in 10s..."; \
        sleep 10; \
    done; \
    echo "[BUILD] uv sync failed after 3 attempts"; \
    exit 1'


# ── Stage 3: Runtime image ───────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="SlideGen" \
      org.opencontainers.image.description="AI-powered presentation generator" \
      org.opencontainers.image.version="0.1.0"

WORKDIR /app

# ── System dependencies + Node.js 22 ────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        fonts-dejavu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Python venv from build stage ─────────────────────────────────────────────
COPY --from=python-deps /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ── Playwright: install Chromium browser + its system deps ───────────────────
# Stores browser to /root/.cache/ms-playwright/ and creates a stable symlink
RUN playwright install chromium --with-deps \
    && CHROMIUM_PATH=$(find /root/.cache/ms-playwright -name "chrome" -type f | head -1) \
    && ln -sf "$CHROMIUM_PATH" /usr/local/bin/chromium-playwright \
    && echo "[PROD] Playwright Chromium at: $CHROMIUM_PATH"

# ── Application source ────────────────────────────────────────────────────────
COPY backend/ ./backend/
COPY migrate_db.py .

# ── Frontend (pre-built static files) ────────────────────────────────────────
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# ── Persistent data directories (content managed via volumes) ─────────────────
RUN mkdir -p \
        static/uploads \
        static/output \
        static/captures \
        static/temp \
        backend/infrastructure/database

# ── Entrypoint ────────────────────────────────────────────────────────────────
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 12008

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:12008/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
