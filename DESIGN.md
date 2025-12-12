# Design Documentation

## Overview

This document explains the architectural design decisions for the Distributed Network Telemetry Processing & Anomaly Detection system. The design prioritizes modularity, type safety, testability, and future extensibility while maintaining simplicity and adherence to Python best practices.

---

## Design Philosophy

### Core Principles

1. **SOLID Principles**: Every module has a single responsibility, depends on abstractions (protocols), and is open for extension but closed for modification
2. **DRY (Don't Repeat Yourself)**: Shared logic is extracted to reusable components without creating god-like modules
3. **Composition Over Inheritance**: Dependencies are injected via protocols rather than inherited through class hierarchies
4. **Protocol-Driven Design**: Use Python protocols for structural typing, enabling flexible implementations and easy testing
5. **Future-Proof Architecture**: Every package is designed to be extracted into a separate repository/library with minimal refactoring

### Key Goals

- **Modularity**: Clear boundaries between services and infrastructure
- **Reusability**: Infrastructure components can be shared across services or extracted to libraries
- **Testability**: Every component can be tested in isolation with clear dependencies
- **Type Safety**: Full type annotations with mypy strict mode compliance
- **Maintainability**: Code is self-documenting with clear structure and comprehensive docstrings

---

## File Structure Design

### High-Level Organization

```
take_home/
├── src/                      # Main source code
│   ├── core/                # Shared domain (minimal)
│   ├── ingest/              # Ingest service (future repo)
│   ├── processor/           # Processor service (future repo)
│   ├── streams/             # Stream infrastructure (future library)
│   ├── storage/             # Storage infrastructure (future library)
│   ├── alerts/              # Alert infrastructure (future library)
│   └── utils/               # Generic utilities (future library)
├── simulator/               # Device simulator (standalone)
├── tests/                   # Test suite (mirrors src/)
├── docker/                  # Container configurations
├── config/                  # Service configurations
└── scripts/                 # Development utilities
```

### Design Rationale

#### 1. Service Isolation (`src/ingest/`, `src/processor/`)

**Decision**: Each service is a self-contained package with its own models, exceptions, and business logic.

**Justification**:
- **Independent Deployment**: Services can be containerized and deployed separately
- **Team Ownership**: Different teams can own different services
- **Scalability**: Each service can scale independently based on load
- **Repository Extraction**: Can be moved to separate repos without breaking dependencies

**Structure**:
```
src/ingest/
├── __init__.py
├── py.typed              # Type information marker
├── main.py               # Service entry point
├── api.py                # HTTP endpoints (FastAPI)
├── service.py            # Business logic
├── models.py             # Ingest-specific models
├── exceptions.py         # Ingest-specific exceptions
└── dependencies.py       # FastAPI dependency injection
```

**Key Pattern**: Each service depends on protocols from `core/protocols.py`, not concrete implementations. This enables:
- Mock implementations for testing
- Swapping implementations (Redis → Kafka) without changing service code
- Clear contracts between services and infrastructure

#### 2. Minimal Core Domain (`src/core/`)

**Decision**: Core package contains ONLY truly shared abstractions and domain models.

**Justification**:
- **Avoid God Modules**: No single `models.py` or `exceptions.py` with unrelated concerns
- **Clear Contracts**: Protocols define interfaces that all services agree on
- **Shared Language**: Domain models represent the universal business concepts (e.g., `TelemetryEvent`)
- **Base Configuration**: Common settings that all services inherit

**What's in Core**:
```python
# core/models.py - ONLY universal domain models
@dataclass(frozen=True, slots=True, kw_only=True)
class TelemetryEvent:
    """Universal telemetry event shared across ALL services."""
    device_id: str
    interface: str
    metric_name: str
    metric_value: float
    timestamp: datetime

# core/protocols.py - Interface definitions
class StreamProtocol(Protocol):
    """Contract for stream operations."""
    async def publish(self, stream: str, data: dict) -> str: ...
    async def consume(self, stream: str, group: str) -> AsyncIterator[Event]: ...

# core/exceptions.py - Base exception hierarchy
class TelemetryError(Exception):
    """Root exception for entire system."""
    pass

class ConfigurationError(TelemetryError):
    """Configuration-related errors across all services."""
    pass
```

**What's NOT in Core**:
- Service-specific models (e.g., `IngestRequest`, `WindowState`)
- Infrastructure-specific models (e.g., `StreamMessage`, `Alert`)
- Service-specific exceptions (e.g., `InvalidPayloadError`)
- Business logic or implementations

#### 3. Distributed Models Pattern

**Decision**: Each package has its own `models.py` containing domain models relevant to that package.

**Justification**:
- **Package Cohesion**: Models are colocated with the code that uses them
- **Repository Extraction**: When extracting a package, all its models come along
- **Avoid Monoliths**: Prevents a single massive models file with unrelated concerns
- **Clear Ownership**: Each package owns its domain models

**Example Distribution**:
```python
# src/core/models.py
class TelemetryEvent:  # Shared across all services

# src/ingest/models.py
class IngestRequest:   # Only used by ingest service
class IngestResponse:  # Only used by ingest service

# src/processor/models.py
class WindowState:     # Only used by processor
class AnomalyResult:   # Only used by processor

# src/streams/models.py
class StreamMessage:   # Only used by stream infrastructure
class ConsumerGroup:   # Only used by stream infrastructure

# src/alerts/models.py
class Alert:           # Only used by alert infrastructure
class AlertSeverity:   # Only used by alert infrastructure
```

**Benefits**:
- Clear boundaries between domains
- Easy to understand what models belong where
- Self-contained packages for extraction

#### 4. Distributed Exceptions Pattern

**Decision**: Each package has its own `exceptions.py` with a hierarchy that inherits from core base exceptions.

**Justification**:
- **Error Domain Isolation**: Exceptions are scoped to the package that raises them
- **Package Self-Containment**: Exception definitions travel with the code
- **Clear Hierarchy**: All exceptions inherit from `core.exceptions.TelemetryError`
- **Specific Error Handling**: Consumers can catch package-specific exceptions

**Exception Hierarchy**:
```python
# core/exceptions.py (base)
TelemetryError
├── ConfigurationError

# ingest/exceptions.py
TelemetryError
└── IngestError
    ├── InvalidPayloadError
    └── StreamPublishError

# processor/exceptions.py
TelemetryError
└── ProcessorError
    ├── AggregationError
    └── StateRecoveryError

# streams/exceptions.py
TelemetryError
└── StreamError
    ├── ConsumerGroupError
    └── BackpressureError
```

**Benefits**:
- Fine-grained error handling: `except InvalidPayloadError:`
- Broad error handling: `except IngestError:`
- System-wide error handling: `except TelemetryError:`
- No god-like exceptions file

#### 5. Infrastructure as Reusable Libraries

**Decision**: Stream, storage, and alert packages are designed as standalone infrastructure libraries.

**Justification**:
- **Reusability**: Multiple services can use the same infrastructure
- **Testability**: Infrastructure can be tested independently
- **Swappability**: Redis can be replaced with Kafka by implementing the same protocol
- **Distribution**: Can be extracted to internal PyPI packages

**Package Structure**:
```
src/streams/                    # Stream infrastructure library
├── __init__.py
├── py.typed                    # Type information for consumers
├── redis_stream.py             # Implements StreamProtocol
├── backpressure.py             # Backpressure management
├── models.py                   # Stream-specific models
└── exceptions.py               # Stream-specific exceptions
```

**Usage Pattern**:
```python
# Service depends on protocol
from src.core.protocols import StreamProtocol

class IngestService:
    def __init__(self, stream: StreamProtocol):
        self._stream = stream  # Any implementation works

# Main wires up concrete implementation
from src.streams.redis_stream import RedisStream

stream = RedisStream(url="redis://localhost")
service = IngestService(stream=stream)
```

**Benefits**:
- Services don't know about Redis
- Easy to mock for testing: `Mock(spec=StreamProtocol)`
- Can swap implementations without changing service code
- Infrastructure logic is isolated and reusable

#### 6. Test Structure Mirrors Source Structure

**Decision**: Tests are organized in a one-to-one mapping with source packages, with package-specific fixtures.

**Justification**:
- **Discoverability**: Finding tests for `src/processor/aggregator.py` is trivial (`tests/processor/test_aggregator.py`)
- **Repository Extraction**: When extracting a package, tests come along with zero refactoring
- **Isolated Fixtures**: Each package has its own `conftest.py` with relevant test fixtures
- **Maintainability**: Clear organization makes it easy to add/update tests

**Structure**:
```
tests/
├── conftest.py                 # Root fixtures (Redis client, etc.)
├── core/
│   ├── conftest.py            # Core-specific fixtures
│   └── test_models.py
├── processor/
│   ├── conftest.py            # Processor-specific fixtures
│   ├── test_worker.py
│   ├── test_aggregator.py
│   └── test_integration.py
└── streams/
    ├── conftest.py            # Stream-specific fixtures
    └── test_redis_stream.py
```

**Fixture Locality**:
```python
# tests/processor/conftest.py
@pytest.fixture
def sample_telemetry_events():
    """Test data specific to processor tests."""
    return [TelemetryEvent(...), TelemetryEvent(...)]

@pytest.fixture
def mock_aggregator():
    """Mock aggregator for processor tests."""
    return Mock(spec=AggregatorProtocol)
```

**Benefits**:
- Tests are colocated with relevant fixtures
- No global fixture pollution
- Package extraction includes all necessary test infrastructure
- Easy to run tests for a specific package: `pytest tests/processor/`

#### 7. Type Safety with py.typed

**Decision**: Every distributable package includes a `py.typed` marker file.

**Justification**:
- **Type Distribution**: When packages are distributed as libraries, consumers get type information
- **IDE Support**: Enables autocomplete and type checking in consuming projects
- **PEP 561 Compliance**: Follows Python standard for distributing type information
- **Developer Experience**: Consumers get the same type safety as monorepo code

**Placement**:
```
src/
├── core/
│   └── py.typed              # Core package exports types
├── streams/
│   └── py.typed              # Stream library exports types
├── storage/
│   └── py.typed              # Storage library exports types
└── alerts/
    └── py.typed              # Alert library exports types
```

**Impact**:
```python
# After extraction: pip install telemetry-streams
from telemetry_streams import RedisStream
from telemetry_streams.models import StreamMessage

# With py.typed:
# ✅ mypy validates types
# ✅ IDE provides autocomplete
# ✅ Type errors caught at development time

# Without py.typed:
# ❌ mypy treats as Any
# ❌ No autocomplete
# ❌ Type errors only at runtime
```

---

## Protocol-Driven Architecture

### Why Protocols Over Abstract Base Classes?

**Decision**: Use Python protocols (PEP 544 structural typing) instead of ABCs.

**Justification**:

1. **Structural Typing**: Classes implement protocols implicitly without inheritance
2. **Duck Typing**: "If it walks like a duck and quacks like a duck, it's a duck"
3. **No Coupling**: Implementations don't need to inherit from a base class
4. **Easier Testing**: Mock objects automatically satisfy protocols
5. **Third-Party Integration**: External libraries can implement our protocols without modification

**Example**:
```python
# core/protocols.py
from typing import Protocol, AsyncIterator

class StreamProtocol(Protocol):
    """Contract for stream operations."""
    
    async def publish(self, stream: str, data: dict) -> str:
        """Publish data to stream."""
        ...
    
    async def consume(
        self, 
        stream: str, 
        group: str
    ) -> AsyncIterator[dict]:
        """Consume messages from stream."""
        ...

# streams/redis_stream.py - Implements protocol implicitly
class RedisStream:
    """Redis Streams implementation (no explicit inheritance)."""
    
    async def publish(self, stream: str, data: dict) -> str:
        # Implementation
        return message_id
    
    async def consume(
        self, 
        stream: str, 
        group: str
    ) -> AsyncIterator[dict]:
        # Implementation
        yield message

# Type checker validates: RedisStream satisfies StreamProtocol ✅
```

**Benefits**:
- No inheritance required
- Can have multiple protocol implementations side-by-side
- Easy to add new protocols without modifying existing code
- Encourages composition over inheritance

---

## Dependency Injection Pattern

### Composition Over Inheritance

**Decision**: Use constructor injection with protocol dependencies rather than inheritance.

**Justification**:
- **Testability**: Dependencies can be easily mocked
- **Flexibility**: Different implementations can be swapped at runtime
- **Clarity**: Dependencies are explicit in the constructor
- **Loose Coupling**: Components depend on abstractions, not concretions

**Example**:
```python
# processor/worker.py
class TelemetryWorker:
    """Processor worker with injected dependencies."""
    
    def __init__(
        self,
        consumer: StreamProtocol,        # Protocol dependency
        aggregator: AggregatorProtocol,  # Protocol dependency
        detector: DetectorProtocol,      # Protocol dependency
        state: StorageProtocol,          # Protocol dependency
        alerter: AlerterProtocol,        # Protocol dependency
    ) -> None:
        """Initialize worker with all dependencies."""
        self._consumer = consumer
        self._aggregator = aggregator
        self._detector = detector
        self._state = state
        self._alerter = alerter
    
    async def process_events(self) -> None:
        """Process events using injected dependencies."""
        async for event in self._consumer.consume("telemetry", "workers"):
            aggregated = await self._aggregator.aggregate(event)
            
            if self._detector.is_anomaly(aggregated):
                await self._alerter.send_alert(aggregated)
            
            await self._state.save(aggregated)

# main.py - Wire up concrete implementations
from src.streams.redis_stream import RedisStream
from src.processor.aggregator import TumblingWindowAggregator
from src.processor.detector import ThresholdDetector
from src.storage.redis_store import RedisStore
from src.alerts.console import ConsoleAlerter

worker = TelemetryWorker(
    consumer=RedisStream(url="redis://localhost"),
    aggregator=TumblingWindowAggregator(window_size=60),
    detector=ThresholdDetector(threshold=90.0),
    state=RedisStore(url="redis://localhost"),
    alerter=ConsoleAlerter(),
)
```

**Testing Benefits**:
```python
# tests/processor/test_worker.py
def test_worker_processes_anomaly():
    # All dependencies are mocks
    mock_consumer = Mock(spec=StreamProtocol)
    mock_aggregator = Mock(spec=AggregatorProtocol)
    mock_detector = Mock(spec=DetectorProtocol)
    mock_state = Mock(spec=StorageProtocol)
    mock_alerter = Mock(spec=AlerterProtocol)
    
    # Configure mocks
    mock_detector.is_anomaly.return_value = True
    
    # Test with mocked dependencies
    worker = TelemetryWorker(
        consumer=mock_consumer,
        aggregator=mock_aggregator,
        detector=mock_detector,
        state=mock_state,
        alerter=mock_alerter,
    )
    
    await worker.process_events()
    
    # Verify interactions
    mock_alerter.send_alert.assert_called_once()
```

---

## Repository Extraction Strategy

### Designed for Future Separation

**Decision**: Every package is designed to be extracted into a separate repository with minimal refactoring.

**Extraction Path**:

#### Phase 1: Monorepo (Current)
```
take_home/
└── src/
    ├── core/
    ├── ingest/
    ├── processor/
    ├── streams/
    ├── storage/
    └── alerts/
```

#### Phase 2: Extract Core Library
```bash
# New repo: telemetry-core
telemetry-core/
├── src/
│   └── telemetry_core/
│       ├── __init__.py
│       ├── py.typed
│       ├── models.py
│       ├── protocols.py
│       ├── config.py
│       └── exceptions.py
├── tests/
├── pyproject.toml
└── README.md

# Publish to PyPI/internal registry
pip install telemetry-core
```

#### Phase 3: Extract Infrastructure Libraries
```bash
# New repo: telemetry-streams
telemetry-streams/
├── src/
│   └── telemetry_streams/
│       ├── __init__.py
│       ├── py.typed
│       ├── redis_stream.py
│       ├── backpressure.py
│       ├── models.py
│       └── exceptions.py
├── tests/
│   └── streams/              # Tests come along!
│       ├── conftest.py       # Fixtures come along!
│       └── test_redis_stream.py
├── pyproject.toml
└── README.md

# Dependencies
telemetry-core>=1.0.0
redis>=5.0.1
```

#### Phase 4: Extract Services
```bash
# New repo: telemetry-ingest
telemetry-ingest/
├── src/
│   └── telemetry_ingest/
│       ├── __init__.py
│       ├── py.typed
│       ├── main.py
│       ├── api.py
│       ├── service.py
│       ├── models.py
│       ├── exceptions.py
│       └── dependencies.py
├── tests/
│   └── ingest/              # Tests come along!
├── Dockerfile
├── pyproject.toml
└── README.md

# Dependencies
telemetry-core>=1.0.0
telemetry-streams>=1.0.0
telemetry-storage>=1.0.0
```

**Migration Checklist**:
- ✅ Copy package directory
- ✅ Copy test directory
- ✅ Update imports (`from src.core` → `from telemetry_core`)
- ✅ Add dependencies to pyproject.toml
- ✅ Verify tests pass
- ✅ Deploy independently

**Zero Code Changes Required**:
- Protocol contracts remain the same
- Business logic unchanged
- Test suite comes along with fixtures
- Type information travels via py.typed

---

## Configuration Strategy

### Layered Configuration

**Decision**: Use Pydantic Settings with YAML files and environment variable overrides.

**Justification**:
- **Type Safety**: Configuration is validated at startup
- **Flexibility**: YAML for complex settings, env vars for deployment
- **12-Factor Compliance**: Environment-based configuration for cloud deployments
- **Inheritance**: Shared settings in base class, service-specific settings in subclasses

**Structure**:
```python
# core/config.py - Base configuration
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    """Base configuration for all services."""
    
    redis_url: str
    log_level: str = "INFO"
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# ingest/config.py - Service-specific configuration
from src.core.config import BaseConfig

class IngestConfig(BaseConfig):
    """Configuration for ingest service."""
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    max_payload_size: int = 1048576  # 1MB
    
    class Config:
        env_prefix = "INGEST_"  # INGEST_API_PORT=8080
```

**Configuration Sources (Priority)**:
1. Environment variables (highest priority)
2. `.env` file
3. YAML configuration file
4. Default values (lowest priority)

**Usage**:
```python
# Load configuration
config = IngestConfig(
    _env_file="config/ingest.yaml"
)

# Environment variable override
# INGEST_API_PORT=9000 python -m src.ingest.main
```

---

## Async Patterns

### Async/Await Throughout

**Decision**: Use async/await for all I/O operations (HTTP, Redis, stream processing).

**Justification**:
- **Performance**: Non-blocking I/O enables high concurrency
- **Scalability**: Single worker can handle many concurrent streams
- **Modern Python**: Leverages Python 3.10+ async capabilities
- **Framework Alignment**: FastAPI and Redis async client are async-native

**Pattern**:
```python
# Async service methods
class IngestService:
    async def ingest_telemetry(
        self, 
        event: TelemetryEvent
    ) -> str:
        """Async ingestion with non-blocking Redis."""
        event_id = await self._stream.publish("telemetry", event.dict())
        return event_id

# Async stream processing
class TelemetryWorker:
    async def process_events(self) -> None:
        """Async event processing with concurrent handling."""
        async for event in self._consumer.consume("telemetry", "workers"):
            # Non-blocking processing
            await self._process_single_event(event)
```

---

## Data Structure Selection

### Optimized for Performance

**Decision**: Use appropriate data structures based on access patterns.

**Patterns**:
```python
# Sets for membership checks
active_devices: set[str] = {"device-01", "device-02"}
if device_id in active_devices:  # O(1) lookup

# Deques for sliding windows
from collections import deque
window_events: deque[TelemetryEvent] = deque(maxlen=100)
window_events.append(event)  # O(1) append with automatic eviction

# Dataclasses for structured data (frozen for immutability)
@dataclass(frozen=True, slots=True, kw_only=True)
class AggregatedMetric:
    device_id: str
    metric_name: str
    avg_value: float
    window_start: datetime
    window_end: datetime

# Enums for constants
class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

---

## Logging Strategy

### Structured Logging

**Decision**: Use structlog for structured, machine-parseable logs.

**Justification**:
- **Observability**: Logs are queryable in log aggregation systems
- **Context**: Rich context attached to log entries
- **Performance**: Structured logs are faster to process
- **Debugging**: Easy to filter and search logs

**Pattern**:
```python
import logging
_log = logging.getLogger(__name__)

# Structured logging with context
_log.info(
    "Processing telemetry event",
    device_id=event.device_id,
    metric_name=event.metric_name,
    metric_value=event.metric_value,
)

# Error logging with exception context
_log.error(
    "Failed to publish to stream",
    stream_name="telemetry",
    error=str(err),
    exc_info=True,
)
```

---

## Trade-Offs and Alternatives

### Decisions and Justifications

#### 1. Protocols vs Abstract Base Classes

**Chosen**: Protocols (structural typing)
**Alternative**: ABCs (nominal typing)

**Trade-off**:
- ✅ More flexible (no inheritance required)
- ✅ Better for third-party integration
- ✅ Cleaner testing (implicit satisfaction)
- ⚠️ Less explicit (no runtime enforcement)
- ⚠️ Requires type checker to validate

**Justification**: Flexibility and testability outweigh the need for runtime validation.

#### 2. Distributed Models vs Central Models

**Chosen**: Distributed models (each package has models.py)
**Alternative**: Central models.py in core/

**Trade-off**:
- ✅ Package self-containment
- ✅ Clear ownership
- ✅ Easy repository extraction
- ⚠️ Potential duplication (mitigated by inheritance)
- ⚠️ More files to navigate

**Justification**: Self-containment and extraction-readiness justify the additional files.

#### 3. Monorepo vs Multi-Repo (Current)

**Chosen**: Monorepo (extraction-ready)
**Alternative**: Start with multiple repositories

**Trade-off**:
- ✅ Simplified development (single clone)
- ✅ Atomic commits across services
- ✅ Easier refactoring
- ⚠️ All services deployed together initially
- ⚠️ Requires discipline for boundaries

**Justification**: For initial development, monorepo provides velocity. Structure enables easy extraction later.

#### 4. Redis Streams vs Kafka

**Chosen**: Redis Streams
**Alternative**: Apache Kafka

**Trade-off**:
- ✅ Simpler deployment (single Redis)
- ✅ Lower operational overhead
- ✅ Sufficient for assignment requirements
- ⚠️ Less mature than Kafka for large scale
- ⚠️ No multi-datacenter replication

**Justification**: Assignment scope doesn't require Kafka complexity. Protocol design enables future migration.

---

## Validation Checklist

### Design Principles Compliance

✅ **SOLID Principles**
- Single Responsibility: Each module/class has one clear purpose
- Open/Closed: Extensible via protocols without modifying core
- Liskov Substitution: All protocol implementations are interchangeable
- Interface Segregation: Focused protocols (Stream, Storage, Alerter separate)
- Dependency Inversion: Depend on protocols, not concrete classes

✅ **DRY Compliance**
- No duplicated logic across services
- Shared abstractions in core
- Reusable infrastructure libraries

✅ **Type Safety**
- Full type annotations (mypy strict mode)
- py.typed markers for distribution
- Protocol-based contracts

✅ **Testability**
- All dependencies injected via protocols
- Tests mirror source structure
- Package-specific fixtures
- 100% coverage achievable

✅ **Reusability**
- Infrastructure as libraries
- Protocol-driven design
- Self-contained packages

✅ **Future-Proof**
- Extraction-ready structure
- Clear boundaries
- Minimal cross-dependencies
- Type information travels with code

✅ **Not Overcomplicated**
- Flat hierarchy (2-3 levels max)
- Only necessary abstractions
- Clear naming conventions
- Self-documenting structure

---

## Conclusion

This design balances immediate implementation needs with long-term maintainability and scalability. Every decision prioritizes:

1. **Developer Experience**: Clear structure, type safety, easy testing
2. **Maintainability**: Self-documenting code, clear boundaries, comprehensive docs
3. **Scalability**: Protocol-driven, extraction-ready, loose coupling
4. **Quality**: Type checking, test coverage, defensive programming

The structure enables rapid development while maintaining production-grade quality and future extensibility.
