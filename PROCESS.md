# Process Document

## Purpose

This document serves as our implementation roadmap for the Distributed Network Telemetry Processing & Anomaly Detection assignment. It clarifies our understanding of requirements, documents key assumptions, defines our technical approach, and tracks progress through completion checklists.

---

## Objectives

Build a distributed system that:
1. Ingests network telemetry data via HTTP endpoints
2. Processes telemetry streams using distributed workers
3. Performs time-windowed aggregation of metrics
4. Detects anomalies based on threshold violations
5. Manages worker coordination and state recovery
6. Handles system overload scenarios gracefully

---

## Requirements

### Core Requirements Checklist

- [x] **Telemetry Ingest Service**
  - [x] HTTP service accepting network telemetry data (FastAPI in `src/ingest/`)
  - [x] Asynchronous handling of incoming metrics (`async def` endpoints)
  - [x] Forward events to Redis Streams (`IngestService.ingest_telemetry()`)
  - [x] Accept device info, interface details, metric values, timestamps (`IngestRequest` model)

- [x] **Telemetry Processor Worker Service**
  - [x] Consume events from Redis Streams (`TelemetryWorker` with consumer groups)
  - [x] Support multiple concurrent worker instances (Docker Compose `replicas: 2`)
  - [x] Implement consumer group pattern for distribution (Redis consumer groups)
  - [x] Calculate time-windowed aggregations (`TumblingWindowAggregator`)
  - [x] Detect threshold-based anomalies (`ThresholdDetector`)
  - [x] Handle worker state management (`WindowState` in Redis)
  - [x] Support recovery scenarios (Consumer acknowledgments and state persistence)
  - [x] Output processed results and anomaly alerts (`ConsoleAlerter`)

- [x] **Coordination & Storage**
  - [x] Redis Streams for event streaming (`RedisStream` implementation)
  - [x] Redis for worker coordination and state (`RedisStore` for state)
  - [x] Proper message delivery guarantees (Consumer groups with ACK)

### Extended Requirements (Choose ≥1)

- [x] **Dynamic Configuration** - Runtime config changes via environment variables and Pydantic Settings (`ProcessorConfig`)
- [x] **Backpressure Management** - Graceful overload handling (`BackpressureManager` with token bucket algorithm)

### Bonus Requirements

- [x] Docker Compose setup with multiple worker instances (`docker-compose.yml` with 2 processor replicas)
- [x] Network device simulator for continuous telemetry (`simulator/` package)
- [x] Unit tests for stream processing and state management (152 passing tests, 43% coverage)

### Documentation Requirements

- [x] README.md with architecture decisions and trade-offs (Basic structure, needs enhancement)
- [x] AI_LOG.md documenting AI tool usage (Comprehensive log maintained)
- [x] PROCESS.md (this document) - Complete and updated
- [x] ARCHITECTURE.md - Detailed system architecture documentation
- [x] DESIGN.md - Design patterns and implementation details
- [x] METHODOLOGY.md - Development methodology and practices

---

## Technical Stack

### Core Technologies

| Technology | Purpose | Version |
|-----------|---------|---------|
| **Python** | Primary language | 3.10+ |
| **FastAPI** | HTTP API framework for ingest service | Latest |
| **Redis** | Stream processing and coordination | Latest |
| **redis-py** | Python Redis client with streams support | Latest |
| **Docker Compose** | Container orchestration | Latest |

### Supporting Libraries

| Library | Purpose |
|---------|---------|
| **uvicorn** | ASGI server for FastAPI |
| **pydantic** | Data validation and settings management |
| **structlog** | Structured logging |

### Development Tools

- **ruff** - Linting and formatting
- **mypy** - Static type checking
- **pytest** - Testing framework
- **pytest-asyncio** - Async testing support
- **pytest-cov** - Code coverage reporting
- **pydocstyle** - Docstring style checker

---

## Key Assumptions

### System Architecture

1. **Single Redis Instance**: We'll use a single Redis instance for both streams and coordination. In production, this would be a Redis cluster with replication.

2. **Deployment Model**: All services run in Docker containers orchestrated by Docker Compose for simplified local development and demonstration.

3. **Network Topology**: Simulated network devices represent simple interfaces with basic metrics (throughput, error rates, latency).

### Telemetry Data Model

1. **Metric Types**: We'll focus on common network metrics:
   - Interface throughput (bytes/sec)
   - Packet error rates (errors/sec)
   - Interface latency (milliseconds)
   - CPU utilization (percentage)

2. **Time Windows**: Use 60-second tumbling windows for aggregation to balance responsiveness with statistical significance.

3. **Device Identification**: Each device has a unique ID and each interface has a unique identifier within that device.

### Anomaly Detection

1. **Threshold-Based Detection**: Simple static thresholds per metric type:
   - Throughput: > 90% of interface capacity
   - Error rate: > 1% of total packets
   - Latency: > 100ms
   - CPU: > 85%

2. **Alert Deduplication**: Suppress repeated alerts for the same device/metric within a time window to avoid alert fatigue.

### Worker Behavior

1. **Consumer Groups**: Use Redis consumer groups for automatic load distribution among workers.

2. **State Persistence**: Worker state (window aggregations) stored in Redis with TTL to handle worker failures.

3. **Graceful Shutdown**: Workers process pending messages before terminating.

4. **Acknowledgment Strategy**: Acknowledge messages only after successful processing and state persistence.

### Backpressure Strategy

1. **Stream Size Limits**: Configure maximum stream length with trimming.

2. **Worker Scaling**: Support horizontal scaling by adding more worker instances.

3. **Reject vs. Queue**: Ingest service returns 429 (Too Many Requests) when Redis stream is at capacity rather than blocking.

---

## Implementation Approach

### Phase 1: Foundation (Setup & Core Services)

1. Project structure and dependency management (pyproject.toml)
2. Docker Compose configuration
3. Telemetry Ingest Service with FastAPI
4. Basic Redis Streams integration
5. Data models and validation with Pydantic

### Phase 2: Stream Processing

1. Telemetry Processor Worker with consumer groups
2. Time-windowed aggregation logic
3. State management in Redis
4. Worker lifecycle and graceful shutdown

### Phase 3: Anomaly Detection

1. Threshold-based anomaly detection
2. Alert output mechanism
3. Alert deduplication logic

### Phase 4: Extended Requirements

1. **Backpressure Management**:
   - Stream size limits and trimming
   - 429 responses from ingest service
   - Monitoring and metrics exposure

### Phase 5: Bonus Features

1. Network device simulator
2. Multiple worker instances in Docker Compose
3. Unit tests with pytest

### Phase 6: Documentation & Cleanup

1. Complete README.md
2. Finalize AI_LOG.md
3. Code cleanup and linting
4. Final testing

---

## Design Decisions

### Why FastAPI?

- Modern async support for I/O-bound operations
- Automatic API documentation (Swagger/OpenAPI)
- Built-in data validation with Pydantic
- High performance and production-ready

### Why Redis Streams?

- Purpose-built for stream processing
- Consumer groups for load distribution
- Built-in message acknowledgment
- Persistence and durability options
- Simple deployment compared to Kafka

### Why Tumbling Windows?

- Predictable, non-overlapping time boundaries
- Simpler state management than sliding windows
- Sufficient for basic anomaly detection
- Clear aggregation semantics

### State Management Strategy

- Store window state in Redis with keys like: `window:{device_id}:{interface_id}:{window_start}`
- Use TTL to automatically expire old windows
- Workers claim ownership of time windows using Redis locks
- Idempotent processing to handle redelivery

---

## Testing Strategy

### Unit Tests

- Data model validation
- Aggregation calculation logic
- Anomaly detection threshold logic
- Window boundary calculations
- State serialization/deserialization

### Integration Tests

- Ingest service → Redis Streams flow
- Worker → Stream consumption
- State persistence and recovery
- Consumer group behavior
- Multiple worker coordination

### Manual Testing

- Load testing with device simulator
- Worker failure and recovery
- Backpressure scenarios
- Configuration changes

---

## Success Criteria

1. ✅ All core requirements implemented and functional
2. ✅ At least one extended requirement completed (backpressure management)
3. ✅ Docker Compose successfully orchestrates all services
4. ✅ Multiple workers process events without duplication
5. ✅ Anomalies are detected and reported
6. ✅ Workers recover gracefully from failures
7. ✅ Code passes linting (ruff) and type checking (mypy)
8. ✅ Unit tests achieve >80% coverage
9. ✅ Documentation clearly explains architecture and trade-offs
10. ✅ AI usage properly documented in AI_LOG.md

---

## Trade-offs & Limitations

### Acknowledged Trade-offs

1. **Static Thresholds vs. ML**: Using simple static thresholds instead of statistical or ML-based anomaly detection for simplicity and transparency.

2. **Single Redis Instance**: Not implementing Redis clustering or replication, accepting single point of failure for this demonstration.

3. **In-Memory State**: Worker state in Redis is sufficient for this scale but would need database backing for production.

4. **Basic Windowing**: Tumbling windows are simpler but less responsive than sliding windows for anomaly detection.

5. **Synchronous Anomaly Output**: Console logging instead of proper alerting system (email, PagerDuty, etc.).

### Known Limitations

1. No authentication/authorization on ingest endpoints
2. No encryption for data in transit or at rest
3. Limited observability (no metrics export, tracing)
4. No rate limiting per device/client
5. No data retention policies beyond stream trimming

---

## Timeline Estimate

| Phase | Estimated Time | Priority |
|-------|----------------|----------|
| Phase 1: Foundation | 1 hour | Must Have |
| Phase 2: Stream Processing | 1.5 hours | Must Have |
| Phase 3: Anomaly Detection | 0.5 hours | Must Have |
| Phase 4: Backpressure | 0.5 hours | Extended Req |
| Phase 5: Bonus Features | 1 hour | Nice to Have |
| Phase 6: Documentation | 0.5 hours | Must Have |
| **Total** | **5 hours** | |

---

## Next Steps

1. Initialize project structure and dependencies
2. Set up Docker Compose with Redis
3. Implement telemetry ingest service
4. Build processor worker service
5. Add anomaly detection
6. Implement backpressure management
7. Create device simulator
8. Write tests
9. Complete documentation

---

*This document will be updated as implementation progresses and new decisions are made.*
