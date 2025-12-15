# Device Simulator Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY simulator/ ./simulator/
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "simulator.main"]
