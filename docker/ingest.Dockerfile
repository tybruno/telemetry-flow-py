# Ingest Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ ./src/
COPY simulator/ ./simulator/

RUN pip install --no-cache-dir -e .

COPY config/ ./config/

CMD ["python", "-m", "src.ingest.main"]
