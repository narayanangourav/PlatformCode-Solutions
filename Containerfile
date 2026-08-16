FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system syncuser && useradd --system --gid syncuser --home-dir /app syncuser

COPY --chown=syncuser:syncuser scripts/ ./scripts/

USER syncuser

ENTRYPOINT ["python", "scripts/sync_leetcode.py"]
