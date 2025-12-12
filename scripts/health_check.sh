#!/bin/bash
# Health check script for services

set -e

# Check ingest service
curl -f http://localhost:8000/api/v1/health || exit 1

# Check Redis
redis-cli ping || exit 1

echo "All services healthy"
