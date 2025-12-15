# Network Telemetry Processing & Anomaly Detection

A distributed system for processing network telemetry data in real-time, performing time-windowed aggregation, and detecting anomalies through threshold-based analysis.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

---

## Overview

This system processes network telemetry data from simulated devices through a distributed pipeline:

1. **Ingest Service**: FastAPI HTTP endpoints receive telemetry data
2. **Redis Streams**: Message queue for distributed event processing
3. **Processor Workers**: Multiple workers consume events, aggregate metrics in time windows, and detect anomalies
4. **Alert System**: Console-based alerts for detected anomalies

### Architecture Diagram

```
┌──────────────┐      HTTP POST      ┌─────────────────┐
│   Simulator  │ ──────────────────> │  Ingest Service │
│  (Devices)   │                     │   (FastAPI)     │
└──────────────┘                     └────────┬────────┘
                                              │
                                              │ Publish
                                              ▼
                                     ┌────────────────────┐
                                     │   Redis Streams    │
                                     │  (Message Queue)   │
                                     └────────┬───────────┘
                                              │
                                              │ Consume (Consumer Groups)
                                              ▼
                              ┌───────────────────────────────┐
                              │    Processor Workers (N)      │
                              │  • Tumbling Window Aggregator │
                              │  • Threshold Detector         │
                              │  • State Management (Redis)   │
                              └────────┬──────────────────────┘
                                       │
                                       │ Alert
                                       ▼
                              ┌────────────────────┐
                              │  Console Alerter   │
                              └────────────────────┘
```

---

## Quick Start

### Prerequisites

- **Docker & Docker Compose**: For containerized deployment
- **Python 3.11+**: For local development
- **Redis**: Included in Docker Compose

### Run the Complete System

```bash
# Start all services (Redis, Ingest, 2 Processor Workers, Simulator)
docker-compose up --build

# View logs from specific service
docker-compose logs -f processor

# Stop all services
docker-compose down
```

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install core dependencies
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Or use Makefile
make install-dev

# Run tests with coverage
make test-cov

# Run linting and type checking
make check

# Auto-fix linting issues
make fix
```

---

## Core Features

### ✅ Core Requirements

1. **Telemetry Ingest Service** (`src/ingest/`)
   - FastAPI HTTP endpoints for receiving telemetry data
   - Asynchronous request handling
   - Data validation using Pydantic models
   - Publishes events to Redis Streams
   - Health check endpoint

2. **Telemetry Processor Workers** (`src/processor/`)
   - Distributed worker pattern with consumer groups
   - Multiple concurrent instances (horizontal scaling)
   - Time-windowed aggregation (tumbling windows, default 60s)
   - Threshold-based anomaly detection
   - State persistence in Redis for fault tolerance
   - Graceful shutdown and recovery

3. **Coordination & Storage**
   - Redis Streams for event distribution
   - Consumer groups for load balancing
   - Message acknowledgment for delivery guarantees
   - State storage with TTL for aggregation windows

### ✅ Extended Requirements (Both Implemented)

1. **Dynamic Configuration**
   - Environment variable-based configuration
   - Pydantic Settings for type-safe config management
   - Runtime changes without service restarts (via env vars)
   - Per-metric threshold configuration

2. **Backpressure Management**
   - Token bucket rate limiting algorithm
   - Graceful throttling under high load
   - Configurable max processing rate
   - Automatic recovery when load decreases

### ✅ Bonus Features

1. **Docker Compose Orchestration**
   - Multi-container setup with service dependencies
   - 2 processor worker replicas for load distribution
   - Health checks and automatic restarts
   - Proper service ordering and startup

2. **Network Device Simulator**
   - Continuous telemetry generation
   - Configurable number of devices and interfaces
   - Realistic metric patterns with occasional anomalies
   - Adjustable anomaly rate and interval

3. **Comprehensive Unit Tests**
   - 325 passing tests across all modules
   - 74% code coverage
   - Pytest with async support
   - Mock-based testing for external dependencies
   - Simulator tests with 98% coverage
   - Full coverage of exceptions, models, and core business logic

---

## Architecture Decisions

### Why FastAPI?

**Decision**: Use FastAPI for the ingest HTTP service

**Rationale**:
- Modern async/await support for high I/O throughput
- Built-in request validation with Pydantic
- Automatic OpenAPI/Swagger documentation
- High performance (comparable to Node.js and Go)
- Type hints integration with editor support

**Trade-offs**:
- ✅ Fast development with auto-generated docs
- ✅ Type safety reduces runtime errors
- ⚠️ Slightly heavier than Flask for simple use cases

### Why Redis Streams?

**Decision**: Use Redis Streams for message queuing and event distribution

**Rationale**:
- Purpose-built for stream processing workloads
- Consumer groups provide automatic load balancing
- Built-in message acknowledgment and redelivery
- Persistence with AOF/RDB for durability
- Simpler operational model than Kafka

**Trade-offs**:
- ✅ Easy to deploy and operate
- ✅ Lower latency than Kafka for small-medium scale
- ✅ Single dependency (Redis) for both streaming and state
- ⚠️ Not designed for petabyte-scale workloads
- ⚠️ Single point of failure without Redis cluster

### Why Tumbling Windows?

**Decision**: Use non-overlapping tumbling windows for aggregation

**Rationale**:
- Simple, predictable time boundaries
- No window state overlap to manage
- Clear semantics for aggregation periods
- Sufficient for threshold-based anomaly detection

**Trade-offs**:
- ✅ Simpler implementation and debugging
- ✅ Lower memory footprint than sliding windows
- ⚠️ Less responsive to gradual changes
- ⚠️ Potential edge effects at window boundaries

### State Management Strategy

**Decision**: Store aggregation state in Redis with TTL

**Rationale**:
- Co-locate state with the message queue
- Atomic operations for consistency
- Automatic cleanup via TTL
- Supports worker restarts and failover

**Trade-offs**:
- ✅ Simple architecture (one Redis instance)
- ✅ Fast state access (in-memory)
- ⚠️ Limited to Redis memory capacity
- ⚠️ Not suitable for long-term historical storage

### Threshold-Based Detection

**Decision**: Use static thresholds for anomaly detection

**Rationale**:
- Transparent and explainable to operators
- No training data or warm-up period required
- Predictable behavior and alerts
- Configurable per metric type

**Trade-offs**:
- ✅ Simple to understand and debug
- ✅ Immediate detection capability
- ✅ Works well for known operational limits
- ⚠️ Cannot adapt to normal traffic patterns
- ⚠️ May have false positives/negatives vs. ML approaches

---

## Project Structure

```
.
├── src/
│   ├── core/              # Shared domain models and protocols
│   │   ├── models.py      # TelemetryEvent data model
│   │   ├── protocols.py   # Interface definitions
│   │   └── config.py      # Base configuration
│   │
│   ├── ingest/            # HTTP ingest service
│   │   ├── api.py         # FastAPI endpoints
│   │   ├── service.py     # Business logic
│   │   ├── models.py      # Request/response models
│   │   └── main.py        # Application entry point
│   │
│   ├── processor/         # Telemetry processor worker
│   │   ├── worker.py      # Main worker orchestration
│   │   ├── config.py      # Worker configuration
│   │   └── main.py        # Worker entry point
│   │
│   ├── aggregation/       # Time-windowed aggregation
│   │   ├── tumbling_window.py  # Tumbling window aggregator
│   │   ├── window_state.py     # State management
│   │   └── models.py           # Aggregation models
│   │
│   ├── detection/         # Anomaly detection
│   │   ├── threshold.py   # Threshold-based detector
│   │   └── models.py      # Detection result models
│   │
│   ├── alerts/            # Alert output
│   │   ├── console.py     # Console alert sink
│   │   └── models.py      # Alert models
│   │
│   ├── consumers/         # Stream consumer infrastructure
│   │   ├── consumer.py    # Message consumer
│   │   ├── backpressure.py  # Rate limiting
│   │   └── error_handler.py # Retry logic
│   │
│   ├── streams/           # Stream abstractions
│   │   └── redis_stream.py  # Redis Streams client
│   │
│   └── storage/           # State storage
│       └── redis_store.py   # Redis storage client
│
├── simulator/             # Device simulator
│   └── main.py           # Telemetry generator
│
├── tests/                # Unit tests (pytest)
├── docker/               # Dockerfiles
├── config/               # Configuration files
│
└── docker-compose.yml    # Multi-container setup
```

---

## Configuration

### Environment Variables

#### Ingest Service
```bash
REDIS_URL=redis://localhost:6379  # Redis connection
INGEST_API_HOST=0.0.0.0           # Bind address
INGEST_API_PORT=8000              # HTTP port
LOG_LEVEL=INFO                     # Logging level
```

#### Processor Worker
```bash
REDIS_URL=redis://localhost:6379           # Redis connection
PROCESSOR_WINDOW_SIZE_SECONDS=60           # Aggregation window
PROCESSOR_DEFAULT_THRESHOLD=80.0           # Default anomaly threshold
PROCESSOR_MAX_RETRIES=3                    # Retry attempts
PROCESSOR_CONSUMER_GROUP=telemetry-processors  # Consumer group name
LOG_LEVEL=INFO
```

#### Simulator
```bash
INGEST_URL=http://localhost:8000  # Ingest service URL
SIMULATOR_NUM_DEVICES=5           # Number of devices
SIMULATOR_INTERVAL_SECONDS=2      # Telemetry interval
SIMULATOR_ANOMALY_RATE=0.1        # Anomaly probability (10%)
```

---

## API Documentation

### Ingest Telemetry

```http
POST /telemetry
Content-Type: application/json

{
  "device_id": "router-01",
  "interface": "eth0",
  "metric_name": "cpu_utilization",
  "metric_value": 75.5,
  "timestamp": "2025-12-13T10:30:00Z"
}
```

**Response** (200 OK):
```json
{
  "message_id": "1234567890-0",
  "status": "accepted"
}
```

### Health Check

```http
GET /health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "uptime_seconds": 3600.5
}
```

---

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Generate HTML coverage report
make test-cov-html
# Open htmlcov/index.html in browser

# Run specific test file
pytest tests/aggregation/test_tumbling_window.py -v

# Run tests matching pattern
pytest tests/ -k "window" -v
```

---

## Development

### Code Quality

```bash
# Run all checks (lint + format + typecheck)
make check

# Auto-fix linting issues
make fix

# Type checking only
make typecheck
```

### Adding New Features

1. **Add tests first** (TDD approach)
2. **Implement feature** following existing patterns
3. **Update documentation** (docstrings, README, ARCHITECTURE.md)
4. **Run checks**: `make check && make test-cov`
5. **Commit with descriptive message**

---

## Monitoring & Observability

### Current Implementation

- **Logging**: Structured logging to stdout/stderr
  - Request/response logging in ingest service
  - Event processing logs in workers
  - Anomaly detection alerts

- **Health Checks**: 
  - HTTP health endpoint (`/health`)
  - Docker healthchecks for container orchestration

### Production Recommendations

For production deployment, consider adding:

1. **Metrics Export**: Prometheus-compatible metrics
   - Request rates and latencies
   - Processing throughput
   - Queue depths
   - Anomaly detection rates

2. **Distributed Tracing**: OpenTelemetry integration
   - End-to-end request tracing
   - Service dependency visualization

3. **Alerting**: PagerDuty/Slack integration
   - Critical anomaly alerts
   - System health alerts
   - SLA violations

4. **Dashboards**: Grafana dashboards
   - System health overview
   - Throughput and latency trends
   - Anomaly history

---

## Known Limitations

1. **Single Redis Instance**
   - No high availability or failover
   - Single point of failure
   - **Production**: Use Redis Cluster or Sentinel

2. **In-Memory State**
   - Limited by Redis memory
   - No long-term persistence
   - **Production**: Add database for historical data

3. **Static Thresholds**
   - Cannot adapt to traffic patterns
   - May produce false positives
   - **Production**: Consider ML-based detection

4. **No Authentication**
   - Open HTTP endpoints
   - No device authentication
   - **Production**: Add API keys, mTLS, or OAuth

5. **Limited Observability**
   - Console-only alerts
   - Basic logging
   - **Production**: Add metrics, tracing, dashboards

---

## Future Enhancements

- [ ] Machine learning-based anomaly detection
- [ ] Redis Cluster support for HA
- [ ] Grafana dashboards for visualization
- [ ] API authentication and rate limiting
- [ ] Historical data persistence (PostgreSQL/TimescaleDB)
- [ ] Alerting integrations (PagerDuty, Slack, email)
- [ ] Dynamic threshold adjustment
- [ ] Multi-region deployment support

---

## Documentation

- **[ASSIGNMENT.md](ASSIGNMENT.md)**: Original assignment requirements
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system architecture
- **[DESIGN.md](DESIGN.md)**: Design patterns and implementation details
- **[METHODOLOGY.md](METHODOLOGY.md)**: Development methodology
- **[PROCESS.md](PROCESS.md)**: Implementation roadmap and decisions
- **[AI_LOG.md](AI_LOG.md)**: AI tool usage documentation

---

## License

This is a take-home assignment project for demonstration purposes.

---

## Author

Tyler Bruno - Take-Home Assignment Submission

**Submission Date**: December 13, 2025