# telemetry-flow-py

A distributed system for processing network telemetry data in real-time, performing time-windowed aggregation, and detecting anomalies through threshold-based analysis.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![Test Coverage: 97%](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](htmlcov/index.html)

---

## About This Assignment

This is a **take-home assignment** demonstrating the design and implementation of a distributed telemetry processing system. The challenge was to build a real-time network monitoring system capable of ingesting device metrics, performing time-windowed aggregation, and detecting anomalies through distributed worker processing.

**Development Approach:**
This project was developed entirely using **AI-assisted development** with GitHub Copilot (Claude Sonnet 4.5), demonstrating modern development practices:
- 100% code written through VS Code Copilot chat and suggestions
- Design-first methodology with specialized Copilot agents (Design Read Only, Design Placeholder Stubs)
- Comprehensive coding standards defined in [`.github/copilot-instructions.md`](.github/copilot-instructions.md)
- AI-generated tests, documentation, and implementation following project-wide standards

**For complete development methodology and AI workflow, see:** [docs/METHODOLOGY.md](docs/METHODOLOGY.md#phase-5-ai-assisted-development-workflow)

**Assignment Requirements:**
- ✅ Distributed telemetry ingest service (HTTP/FastAPI)
- ✅ Stream-based event processing (Redis Streams with consumer groups)
- ✅ Multiple concurrent processor workers with load distribution
- ✅ Time-windowed metric aggregation (60-second tumbling windows)
- ✅ Threshold-based anomaly detection with alerts
- ✅ Dynamic configuration and backpressure management
- ✅ Docker Compose orchestration with device simulator
- ✅ Comprehensive testing (544 tests, 97% coverage)
   - 539 unit tests (fast, no external dependencies)
   - 5 integration tests (Redis-based, require Docker)

**For complete assignment details and original requirements, see:** [ASSIGNMENT.md](ASSIGNMENT.md)

---

## Overview

This system processes network telemetry data from simulated devices through a distributed pipeline:

1. **Ingest Service**: FastAPI HTTP endpoints receive telemetry data
2. **Redis Streams**: Message queue for distributed event processing
3. **Processor Workers**: Multiple workers consume events, aggregate metrics in time windows, and detect anomalies
4. **Alert System**: Console-based alerts for detected anomalies

**For detailed system architecture and component interactions, see:** [ARCHITECTURE.md](docs/ARCHITECTURE.md)

**For design philosophy and architectural decisions, see:** [DESIGN.md](docs/DESIGN.md)

---

## Quick Start

### Prerequisites

- **Docker & Docker Compose**: For containerized deployment
- **Python 3.10+**: For local development
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

3. **Comprehensive Testing**
   - **544 total tests** across all modules (539 passing)
   - **97% code coverage** with detailed HTML reports
   - **Unit tests** (539+ tests) - Fast, isolated, no external dependencies
   - **Integration tests** (5 tests) - Real Redis interactions, Docker-based
   - Pytest with async support and pytest-asyncio
   - Mock-based testing for external dependencies
   - 100% coverage on core modules (redis_stream, storage, aggregation, detection)
   - Comprehensive edge case and error scenario testing
   - Custom pytest markers for test categorization

4. **CI/CD Pipeline**
   - Automated testing across Python 3.10, 3.11, 3.12
   - Automated linting (ruff) and type checking (mypy)
   - Automated PyPI publishing on GitHub releases
   - OpenID Connect (OIDC) trusted publishing (no API tokens)
   - TestPyPI support for pre-release validation

---

## Architecture & Design

This project follows a **design-first methodology** with comprehensive architectural planning. Key architectural decisions include:

- **Service Isolation**: Ingest and Processor services are self-contained packages
- **Protocol-Driven Design**: Services depend on abstractions (protocols), not implementations  
- **Composition Over Inheritance**: Dependencies injected via constructors for testability
- **Tumbling Windows**: Non-overlapping time windows for metric aggregation
- **Stream Partitioning**: Consistent hashing for horizontal scaling with data locality

**For detailed architectural decisions and trade-offs, see:** [DESIGN.md](docs/DESIGN.md)

**For complete system architecture and package organization, see:** [ARCHITECTURE.md](docs/ARCHITECTURE.md)

**For development methodology and practices, see:** [METHODOLOGY.md](docs/METHODOLOGY.md)

**For implementation roadmap and requirements tracking, see:** [PROCESS.md](docs/PROCESS.md)

---

## Configuration

Configuration is managed through environment variables and Pydantic Settings for type-safe runtime configuration. Each service supports configuration via:

1. Environment variables (highest priority)
2. `.env` files
3. YAML config files in `config/`
4. Default values (lowest priority)

### Key Environment Variables

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

**For detailed configuration options and examples, see:** [ARCHITECTURE.md](docs/ARCHITECTURE.md#configuration)

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

## Development

For comprehensive development guidance including code quality standards, testing requirements, adding new features, and publishing to PyPI:

**See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete development guide.**

### Quick Reference

```bash
make check        # Run all checks (lint + format + typecheck)
make test         # Run all tests with coverage
make fix          # Auto-fix linting issues
make docker-up    # Start Docker services
make all          # Run all checks and tests
```

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

## Known Limitations - No high availability; use Redis Cluster in production
2. **In-Memory State** - Limited by Redis memory; add database for historical data in production
3. **Static Thresholds** - Cannot adapt to traffic patterns; consider ML-based detection in production
4. **No Authentication** - Open HTTP endpoints; add API keys, mTLS, or OAuth in production
5. **Limited Observability** - Console-only alerts; add metrics, tracing, dashboards in production

**For complete list of trade-offs and production recommendations, see:** [DESIGN.md](docs/DESIGN.md) and [ARCHITECTURE.md](docs/ARCHITECTURE.md#monitoring-and-observability)
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

This project includes comprehensive documentation organized for different audiences:

- **[README.md](README.md)** (this file): Quick start and overview
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Development setup, code quality standards, testing, and contributing guidelines
- **[ASSIGNMENT.md](ASSIGNMENT.md)**: Original take-home assignment requirements
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System architecture, data flow, and deployment
- **[DESIGN.md](docs/DESIGN.md)**: Design decisions and trade-offs
- **[METHODOLOGY.md](docs/METHODOLOGY.md)**: Development methodology and practices
- **[PROCESS.md](docs/PROCESS.md)**: Implementation roadmap and success criteria
- **[AI_LOG.md](docs/AI_LOG.md)**: AI tool usage and interaction history
- **[docs/README.md](docs/README.md)**: Complete documentation index

---

## License

This is a take-home assignment project for demonstration purposes.

---

## Author

Tyler Bruno - Take-Home Assignment Submission

**Submission Date**: December 15, 2025
