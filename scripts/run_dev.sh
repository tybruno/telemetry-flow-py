#!/bin/bash
# Development runner script

set -e

echo "Starting telemetry system in development mode..."

# Start Redis in background
redis-server --daemonize yes

# Start ingest service
python -m src.ingest.main &
INGEST_PID=$!

# Start processor workers
python -m src.processor.main &
PROCESSOR_PID=$!

# Trap exit to cleanup
trap "kill $INGEST_PID $PROCESSOR_PID; redis-cli shutdown" EXIT

wait
