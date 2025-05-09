ARG PYTHON_VERSION=3.13
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv pip install --system -r requirements.txt

# Create Static/Media/Logging Files Directory
RUN mkdir -p /app/staticfiles && \
    mkdir -p /app/media && \
    mkdir -p /app/logs && \
    touch /app/logs/general.log && \
    chown -R appuser:appuser /app/staticfiles && \
    chown -R appuser:appuser /app/media && \
    chown -R appuser:appuser /app/logs

# Install libpq (PostgreSQL client library)
RUN apt-get update && apt-get install -y \
    nano \
    curl

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY .. .

# Expose the port that the application listens on.
EXPOSE 8000

# Check that Django Server is running
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=10 CMD docker/healthcheck.sh

# Run the application
ENTRYPOINT ["docker/entrypoint.sh"]
