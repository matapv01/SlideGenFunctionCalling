# ── Stage 1: Build frontend ──────────────────────────────────────────────────
FROM --platform=linux/amd64 node:22-alpine AS frontend-builder

WORKDIR /app

# Install dependencies (copy lockfile first for layer caching)
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci --legacy-peer-deps

# Inject API base URL at build time so Vite bakes it into the bundle
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build production bundle
COPY frontend/ ./frontend/
RUN cd frontend && npm run build


# ── Stage 2: Build Python dependencies ──────────────────────────────────────
FROM --platform=linux/amd64 python:3.11-slim AS python-deps

WORKDIR /app

# Install uv
RUN pip install uv --no-cache-dir

# Install Python deps into a virtualenv (lockfile ensures reproducibility)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev


# ── Stage 3: Runtime image ───────────────────────────────────────────────────
FROM --platform=linux/amd64 python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="SlideGen" \
      org.opencontainers.image.description="AI-powered presentation generator" \
      org.opencontainers.image.version="0.1.0"

WORKDIR /app

# ── System dependencies + Node.js 22 ────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Python venv from build stage ─────────────────────────────────────────────
COPY --from=python-deps /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ── Playwright: install Chromium browser + its system deps ───────────────────
# apt-get update must re-run here because lists were cleaned in the previous RUN
RUN apt-get update \
    && playwright install chromium --with-deps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && CHROMIUM_PATH=$(find /root/.cache/ms-playwright -name "chrome" -type f | head -1) \
    && ln -sf "$CHROMIUM_PATH" /usr/local/bin/chromium-playwright \
    && echo "[Dockerfile] Playwright Chromium at: $CHROMIUM_PATH"

# ── Puppeteer: skip its own Chromium download, reuse Playwright's ─────────────
# Saves ~400MB image size; system deps already satisfied above
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium-playwright

# ── Application source ────────────────────────────────────────────────────────
COPY backend/ ./backend/
COPY migrate_db.py .

# ── Converter Node.js deps ────────────────────────────────────────────────────
# PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true → Puppeteer will NOT download Chromium here
RUN cd backend/infrastructure/converter && npm install --legacy-peer-deps

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
