FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY main.py display.py ./

# Data files are mounted as a volume at runtime
VOLUME ["/app/data"]
ENV SEEN_FILE=/app/data/seen_ids.json
ENV NOTICES_FILE=/app/data/water_notices.jsonl

# Install cron
RUN apt-get update && apt-get install -y --no-install-recommends cron && rm -rf /var/lib/apt/lists/*

# Run every hour
RUN echo "0 * * * * cd /app && uv run python main.py >> /var/log/pwa-noti.log 2>&1" | crontab -

CMD ["cron", "-f"]
