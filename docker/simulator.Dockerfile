# Device Simulator Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY simulator/ ./simulator/
COPY src/core/ ./src/core/

CMD ["python", "-m", "simulator.main"]
