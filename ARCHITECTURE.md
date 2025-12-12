# System Architecture

## Overview

The Distributed Network Telemetry Processing & Anomaly Detection system consists of three main components that communicate via Redis Streams:

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
                                              │ Consume
                                              ▼
                                     ┌────────────────────┐
                                     │ Processor Workers  │
                                     │ (Event Processing) │
                                     └────────┬───────────┘
                                              │
                                              │ Store/Alert
                                              ▼
                                     ┌────────────────────┐
                                     │  Redis Storage +   │
                                     │  Alert System      │
                                     └────────────────────┘
```

---

## Package Organization

### 1. Core (`src/core/`)

**Purpose**: Shared domain models, protocols (interfaces), and base configurations

**What It Contains**:
- `models.py`: Universal data structures (`TelemetryEvent`)
- `protocols.py`: Interface definitions (`StreamProtocol`, `StorageProtocol`, etc.)
- `exceptions.py`: Base exception hierarchy
- `config.py`: Base configuration class

**Used By**: All services and infrastructure packages

**Communication**: Provides contracts, doesn't communicate

**Entry Point**: None (library only)

---

### 2. Ingest Service (`src/ingest/`)

**Purpose**: HTTP API for receiving telemetry data from devices

**What It Contains**:
- `main.py`: FastAPI application entry point
- `api.py`: HTTP endpoints (`POST /telemetry`)
- `service.py`: Business logic for ingestion
- `models.py`: Request/response models
- `dependencies.py`: FastAPI dependency injection

**Communication**:
- **Input**: HTTP POST requests from devices/simulator
- **Output**: Publishes to Redis Streams (`telemetry` stream)

**Dependencies**:
- `core.protocols.StreamProtocol`: To publish events
- `streams.redis_stream.RedisStream`: Concrete Redis implementation

**Entry Points**: 
```bash
# As Python module (with __main__.py)
python -m src.ingest

# Direct module execution
python -m src.ingest.main

# Console script (after pip install)
telemetry-ingest

# Via docker-compose
docker-compose up ingest
```

**Flow**:
1. Receive HTTP POST with telemetry data
2. Validate payload structure
3. Convert to `TelemetryEvent` domain model
4. Publish to Redis Streams
5. Return acknowledgment with message ID

---

### 3. Processor Workers (`src/processor/`)

**Purpose**: Orchestrate event processing using consumer, aggregation, and detection libraries

**What It Contains**:
- `main.py`: Worker entry point
- `worker.py`: Processing orchestrator (uses libraries)
- `config.py`: Processor-specific configuration
- `models.py`: Processor-specific models
- `exceptions.py`: Processor-specific exceptions

**Communication**:
- **Input**: Consumes from Redis Streams (`telemetry` stream, `telemetry-processors` consumer group)
- **Output**: 
  - Stores aggregated state to Redis Storage
  - Sends alerts via `AlerterProtocol`

**Dependencies**:
- `consumers.consumer.TelemetryConsumer`: Generic stream consumer
- `aggregation.tumbling_window.TumblingWindowAggregator`: Windowed aggregation
- `detection.threshold.ThresholdDetector`: Anomaly detection
- `core.protocols.StorageProtocol`: To persist state
- `core.protocols.AlerterProtocol`: To send alerts
- `streams.redis_stream.RedisStream`: Concrete stream implementation
- `storage.redis_store.RedisStore`: Concrete storage implementation
- `alerts.console.ConsoleAlerter`: Console alert implementation

**Entry Points**:
```bash
# As Python module (with __main__.py)
python -m src.processor

# Direct module execution
python -m src.processor.main

# Console script (after pip install)
telemetry-processor

# Via docker-compose
docker-compose up processor
```

**Flow**:
1. Consumer library: Consume events from Redis Streams (XREADGROUP)
2. Consumer library: Deserialize raw message to `TelemetryEvent`
3. Aggregation library: Aggregate events in time windows (e.g., 60-second windows)
4. Detection library: Detect anomalies using threshold detection
5. Store aggregated metrics to Redis
6. Send alerts for detected anomalies
7. Consumer library: Acknowledge message (XACK)

---

### 4. Consumer Infrastructure (`src/consumers/`)

**Purpose**: Reusable stream consumer library with robust error handling and message processing

**What It Contains**:
- `consumer.py`: Generic stream consumer with composition pattern
- `deserializer.py`: Message parsing and validation
- `error_handler.py`: Exponential backoff retry logic
- `models.py`: Consumer-specific models
- `exceptions.py`: Consumer-specific exceptions

**Communication**:
- Wraps `StreamProtocol` for stream operations
- Used by Processor service and can be used by any service needing stream consumption

**Dependencies**:
- `core.protocols.StreamProtocol`: Stream operations interface
- `streams.backpressure.BackpressureManager`: Rate limiting

**Entry Point**: None (library only)

**Key Features**:
- Complete pipeline: consume → deserialize → validate → acknowledge
- Exponential backoff retry for transient failures
- Backpressure management for overload protection
- Error classification (transient vs permanent)
- Generic design works with any domain model

---

### 5. Aggregation Infrastructure (`src/aggregation/`)

**Purpose**: Reusable time-windowed aggregation library for metric processing

**What It Contains**:
- `base_aggregator.py`: Abstract base with shared window utilities
- `tumbling_window.py`: Tumbling window aggregator implementation
- `state.py`: Window state management
- `models.py`: Aggregation-specific models (`WindowState`, `AggregatedMetric`)
- `exceptions.py`: Aggregation-specific exceptions

**Communication**:
- Used by Processor service and can be used by any service needing aggregation
- Stateless design - state managed externally via `StorageProtocol`

**Dependencies**:
- `core.models.TelemetryEvent`: Input event type (can be generalized)

**Entry Point**: None (library only)

**Key Features**:
- Configurable window sizes (default: 60 seconds)
- Statistical calculations: avg, min, max, stddev, count
- Window state tracking with timestamp boundaries
- Generic design works with any metric stream

---

### 6. Detection Infrastructure (`src/detection/`)

**Purpose**: Reusable anomaly detection library with multiple strategies

**What It Contains**:
- `base_detector.py`: Abstract base with shared detection utilities
- `threshold.py`: Threshold-based detector implementation
- `models.py`: Detection-specific models (`AnomalyResult`)
- `exceptions.py`: Detection-specific exceptions

**Communication**:
- Used by Processor service and can be used by any service needing anomaly detection
- Stateless design - operates on aggregated metrics

**Dependencies**:
- `aggregation.models.AggregatedMetric`: Input metric type

**Entry Point**: None (library only)

**Key Features**:
- Threshold-based detection (configurable per metric)
- Extensible for ML-based detection, statistical methods, etc.
- Severity classification (low, medium, high, critical)
- Generic design works with any metric type

---

### 7. Streams Infrastructure (`src/streams/`)

**Purpose**: Reusable message streaming infrastructure (implements `StreamProtocol`)

**What It Contains**:
- `redis_stream.py`: Redis Streams implementation with at-least-once delivery
- `backpressure.py`: Rate limiting and backpressure management
- `models.py`: Stream-specific models (`StreamMessage`, `ConsumerGroup`)
- `exceptions.py`: Stream-specific exceptions

**Communication**:
- Wraps Redis client for stream operations
- Used by both Ingest and Processor services

**Dependencies**:
- `redis.asyncio`: Async Redis client
- `core.protocols.StreamProtocol`: Interface it implements

**Entry Point**: None (library only)

**Key Operations**:
- `publish()`: Add messages to stream (XADD)
- `consume()`: Read messages in consumer group (XREADGROUP)
- `acknowledge()`: Mark messages as processed (XACK)
- `create_consumer_group()`: Setup distributed consumers (XGROUP CREATE)

---

### 8. Storage Infrastructure (`src/storage/`)

**Purpose**: Reusable state persistence infrastructure (implements `StorageProtocol`)

**What It Contains**:
- `base.py`: `BaseStorage` ABC with shared validation
- `redis_store.py`: Redis key-value storage implementation
- `models.py`: Storage-specific models
- `exceptions.py`: Storage-specific exceptions

**Communication**:
- Wraps Redis client for key-value operations
- Used by Processor for state persistence

**Dependencies**:
- `redis.asyncio`: Async Redis client
- `core.protocols.StorageProtocol`: Interface it implements

**Entry Point**: None (library only)

**Key Operations**:
- `store()`: Save data (SET)
- `retrieve()`: Get data (GET)
- `delete()`: Remove data (DEL)

---

### 9. Alerts Infrastructure (`src/alerts/`)

**Purpose**: Reusable alert delivery infrastructure (implements `AlerterProtocol`)

**What It Contains**:
- `base.py`: `BaseAlerter` ABC with shared formatting
- `console.py`: Console/stdout alert implementation
- `models.py`: Alert-specific models (`Alert`, `AlertSeverity`)
- `exceptions.py`: Alert-specific exceptions

**Communication**:
- Used by Processor to send alerts
- Can be extended for email, PagerDuty, Slack, etc.

**Dependencies**:
- `core.protocols.AlerterProtocol`: Interface it implements

**Entry Point**: None (library only)

**Key Operations**:
- `send_alert()`: Deliver alert notification

---

### 10. Simulator (`simulator/`)

**Purpose**: Simulate network devices sending telemetry data

**What It Contains**:
- `main.py`: Simulator entry point
- Device simulation logic for testing

**Communication**:
- **Output**: Sends HTTP POST requests to Ingest Service

**Dependencies**:
- `httpx` or `requests`: HTTP client

**Entry Points**:
```bash
# As Python module (with __main__.py)
python -m simulator

# Direct module execution
python -m simulator.main

# Console script (after pip install)
telemetry-simulator

# Via docker-compose
docker-compose up simulator
```

**Flow**:
1. Generate synthetic telemetry data
2. POST to Ingest Service at `/telemetry`
3. Simulate multiple devices and interfaces

---

## Data Flow

### Complete Telemetry Pipeline

```
1. Device/Simulator
   └─> HTTP POST /telemetry
       {
         "device_id": "router-01",
         "interface": "eth0",
         "metric_name": "packet_loss_rate",
         "metric_value": 0.05,
         "timestamp": "2025-12-12T10:30:00Z"
       }

2. Ingest Service
   ├─> Validate payload
   ├─> Create TelemetryEvent domain model
   └─> Publish to Redis Streams
       XADD telemetry * device_id router-01 interface eth0 ...

3. Redis Streams (Message Queue)
   └─> Store message in stream
       Messages available to consumer group

4. Processor Worker (orchestrates libraries)
   ├─> [Consumer Library] Consume message (XREADGROUP telemetry telemetry-processors worker-1)
   ├─> [Consumer Library] Deserialize to TelemetryEvent
   ├─> [Aggregation Library] Aggregate in time window (e.g., 60s window)
   │   └─> Calculate: avg, min, max, stddev, count
   ├─> [Detection Library] Detect anomalies (threshold-based)
   ├─> Store aggregated metrics (Redis SET)
   ├─> Send alerts if anomaly detected
   └─> [Consumer Library] Acknowledge message (XACK)

5. Redis Storage
   └─> Persist aggregated metrics and window state

6. Alert System
   └─> Console output (or email/PagerDuty in production)
```

---

## Protocol-Driven Communication

Services communicate through well-defined protocols (interfaces):

### StreamProtocol
```python
class StreamProtocol(Protocol):
    async def publish(stream: str, data: dict) -> str: ...
    async def consume(stream: str, group: str) -> AsyncIterator[dict]: ...
    async def acknowledge(stream: str, group: str, message_id: str) -> None: ...
```

**Implementers**: `RedisStream`
**Consumers**: `IngestService`, `TelemetryConsumer`

### StorageProtocol
```python
class StorageProtocol(Protocol):
    async def store(key: str, value: Any) -> None: ...
    async def retrieve(key: str) -> Optional[Any]: ...
```

**Implementers**: `RedisStore`
**Consumers**: `TelemetryWorker`

### AlerterProtocol
```python
class AlerterProtocol(Protocol):
    async def send_alert(alert: Alert) -> None: ...
```

**Implementers**: `ConsoleAlerter`
**Consumers**: `TelemetryWorker`

---

## Running the System

### Development (Local)

```bash
# Terminal 1: Start Redis
docker-compose up redis

# Terminal 2: Start Ingest Service
python -m src.ingest  # or: telemetry-ingest

# Terminal 3: Start Processor Worker
python -m src.processor  # or: telemetry-processor

# Terminal 4: Run Simulator
python -m simulator  # or: telemetry-simulator
```

### Production (Docker Compose)

```bash
# Start all services
docker-compose up

# Services start in order:
# 1. Redis (infrastructure)
# 2. Ingest Service (waits for Redis)
# 3. Processor Workers (wait for Redis + Ingest)
# 4. Simulator (waits for Ingest)
```

### Individual Services

```bash
# Ingest only
docker-compose up ingest

# Processor only
docker-compose up processor

# Scale processor workers
docker-compose up --scale processor=3
```

---

## Configuration

Each service loads configuration from:
1. Environment variables (highest priority)
2. `.env` file
3. YAML config files in `config/`
4. Default values (lowest priority)

### Example: Ingest Configuration

```bash
# Environment variables
export INGEST_API_PORT=8000
export REDIS_URL=redis://localhost:6379

# Or .env file
INGEST_API_PORT=8000
REDIS_URL=redis://localhost:6379
```

### Example: Processor Configuration

```bash
# Environment variables
export PROCESSOR_WINDOW_SIZE_SECONDS=60
export PROCESSOR_DEFAULT_THRESHOLD=80.0
export PROCESSOR_MAX_RETRIES=3

# Or .env file
PROCESSOR_WINDOW_SIZE_SECONDS=60
PROCESSOR_DEFAULT_THRESHOLD=80.0
PROCESSOR_MAX_RETRIES=3
```

---

## Deployment Architecture

### Single Node (Development)
```
┌─────────────────────────────────────┐
│          Single Host                │
│  ┌──────────┐  ┌────────────────┐  │
│  │  Redis   │  │  Ingest (8000) │  │
│  └──────────┘  └────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Processor Workers (x3)      │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Multi-Node (Production)
```
┌──────────────────┐
│  Load Balancer   │
└────────┬─────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐
│Ingest 1│ │Ingest 2│ │Ingest 3│
└────┬───┘ └────┬───┘ └────┬───┘
     │          │          │
     └──────────┴──────────┘
                │
                ▼
     ┌──────────────────────┐
     │   Redis Cluster      │
     │  (Streams + Storage) │
     └──────────┬───────────┘
                │
     ┌──────────┴──────────┬──────────┐
     ▼                     ▼          ▼
┌────────────┐      ┌────────────┐ ┌────────────┐
│Processor 1 │      │Processor 2 │ │Processor 3 │
│(worker-01) │      │(worker-02) │ │(worker-03) │
└────────────┘      └────────────┘ └────────────┘
```

---

## Key Design Patterns

### 1. Protocol-Driven Design
- Services depend on protocols (interfaces), not concrete implementations
- Enables swapping Redis for Kafka without changing service code
- Easy mocking for tests

### 2. Composition Over Inheritance
- Dependencies injected via constructor
- Worker composes consumer, aggregator, detector, storage, alerter
- Each component has single responsibility

### 3. Distributed Models
- Each package owns its domain models
- Avoids monolithic `models.py` files
- Enables clean package extraction

### 4. Consumer Groups for Scalability
- Multiple processor workers in same consumer group
- Redis distributes messages across workers
- Automatic load balancing

### 5. At-Least-Once Delivery
- Messages acknowledged after successful processing
- Failed messages retry automatically
- Ensures no data loss

---

## Extensibility

### Adding New Alert Channels

```python
# alerts/email.py
class EmailAlerter:
    """Email alert implementation."""
    
    async def send_alert(self, alert: Alert) -> None:
        # Send via SMTP
        pass

# Wire up in processor main
alerter = EmailAlerter(smtp_config)
worker = TelemetryWorker(alerter=alerter, ...)
```

### Adding New Anomaly Detectors

```python
# processor/ml_detector.py
class MLDetector:
    """Machine learning-based detector."""
    
    def detect(self, metric: AggregatedMetric) -> Anomaly | None:
        # Use trained model
        pass

# Wire up in processor main
detector = MLDetector(model_path)
worker = TelemetryWorker(detector=detector, ...)
```

### Migrating to Kafka

```python
# streams/kafka_stream.py
class KafkaStream:
    """Kafka implementation of StreamProtocol."""
    
    async def publish(self, topic: str, data: dict) -> str:
        # Kafka producer
        pass
    
    async def consume(self, topic: str, group: str) -> AsyncIterator[dict]:
        # Kafka consumer
        pass

# Wire up in services
stream = KafkaStream(brokers=["localhost:9092"])
service = IngestService(stream=stream)
```

---

## Monitoring and Observability

### Metrics to Track

**Ingest Service**:
- Request rate (requests/sec)
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Stream publish success rate

**Processor Workers**:
- Event processing rate (events/sec)
- Processing latency (event time to completion)
- Anomaly detection rate
- Alert delivery success rate
- Consumer lag (messages pending)

**Infrastructure**:
- Redis memory usage
- Redis stream length
- Consumer group pending messages
- Redis connection pool saturation

### Health Checks

```bash
# Ingest service health
curl http://localhost:8000/health

# Redis health
redis-cli PING

# Stream monitoring
redis-cli XINFO STREAM telemetry
redis-cli XINFO GROUPS telemetry
```

---

## Summary

The architecture follows a clean separation of concerns:

1. **Core**: Shared contracts and domain
2. **Services**: Business logic (Ingest, Processor)
3. **Infrastructure**: Reusable components (Streams, Storage, Alerts)
4. **Simulator**: Testing tool

Communication flows through:
- **HTTP**: Devices → Ingest
- **Redis Streams**: Ingest → Processor
- **Redis Storage**: Processor → State persistence
- **Alerts**: Processor → Alert channels

Each component is:
- **Independently deployable**
- **Horizontally scalable**
- **Protocol-driven for flexibility**
- **Testable in isolation**
