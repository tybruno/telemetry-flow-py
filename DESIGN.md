# Design Documentation

## Overview

This document explains **WHY** architectural decisions were made and **HOW** design patterns are applied in the Distributed Network Telemetry Processing & Anomaly Detection system. It focuses on design philosophy, technical rationale, and trade-offs.

**For WHAT the system does and WHERE components are located, see:** [ARCHITECTURE.md](ARCHITECTURE.md)

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

## Architectural Decisions and Rationale

### 1. Why Service Isolation?

**Decision**: Each service (Ingest, Processor) is a self-contained package with its own models, exceptions, and business logic.

**Rationale**:
- **Independent Deployment**: Services can be containerized and deployed separately, allowing different release cycles
- **Team Ownership**: Different teams can own different services without stepping on each other's toes
- **Scalability**: Each service can scale independently based on load (scale ingest separate from processing)
- **Repository Extraction**: Can be moved to separate repos without breaking dependencies or requiring massive refactoring

**Alternative Considered**: Monolithic service with shared models
- ❌ **Rejected**: Creates tight coupling, prevents independent scaling, makes repo extraction difficult

**Trade-offs**:
- ✅ **Pro**: Clear boundaries, independent deployment, team autonomy
- ⚠️ **Con**: More orchestration complexity (Docker Compose, Kubernetes)
- ⚠️ **Con**: Network overhead between services

**Justification**: For distributed systems, the benefits of independence outweigh orchestration complexity.

---

### 2. Why Minimal Core Domain?

**Decision**: Core package contains ONLY truly shared abstractions (protocols, base exceptions, universal models).

**Rationale**:
- **Avoid God Modules**: Prevents a single massive `models.py` or `exceptions.py` with unrelated concerns
- **Clear Contracts**: Protocols define interfaces that all services agree on without implementation details
- **Shared Language**: Domain models represent universal business concepts (`TelemetryEvent`) used everywhere
- **Minimal Coupling**: Services depend only on contracts, not on each other's implementation

**What Belongs in Core**:
```python
✅ TelemetryEvent       # Universal domain model shared by ALL services
✅ StreamProtocol       # Interface contract for stream operations
✅ TelemetryError       # Root exception for hierarchy
✅ BaseConfig           # Common configuration settings

❌ IngestRequest        # Service-specific model (belongs in ingest/)
❌ WindowMetrics        # Library-specific model (belongs in aggregation/)
❌ InvalidPayloadError  # Service-specific exception (belongs in ingest/)
```

**Alternative Considered**: Everything in core for "easy imports"
- ❌ **Rejected**: Creates tight coupling, violates single responsibility, prevents package extraction

**Trade-offs**:
- ✅ **Pro**: Package independence, clear ownership, extraction-ready
- ⚠️ **Con**: More `models.py` files to navigate (mitigated by IDE tools)

**Justification**: Self-containment and extraction-readiness justify the additional files.

---

### 3. Why Distributed Models Pattern?

**Decision**: Each package has its own `models.py` containing domain models relevant to that package.

**Rationale**:
- **Package Cohesion**: Models are colocated with the code that uses them
- **Repository Extraction**: When extracting a package, all its models come along automatically
- **Clear Ownership**: No confusion about which team owns which models
- **Avoid Monoliths**: Prevents a single file with 50+ unrelated data classes

**Example Distribution**:
```python
src/core/models.py          # Shared: TelemetryEvent
src/ingest/models.py        # Ingest-specific: IngestRequest, IngestResponse
src/aggregation/models.py   # Aggregation-specific: WindowMetrics, WindowBounds
src/detection/models.py     # Detection-specific: AnomalyResult
src/processor/models.py     # Processor-specific: TelemetryWindowKey
```

**Alternative Considered**: Central `models.py` in core
- ❌ **Rejected**: Creates coupling (processor imports ingest models), violates cohesion

**Trade-offs**:
- ✅ **Pro**: Self-contained packages, clear boundaries, easy extraction
- ⚠️ **Con**: Potential duplication (mitigated by inheritance from core models)
- ⚠️ **Con**: More files to track

**Justification**: Cohesion and extraction-readiness are more important than file count.

---

### 4. Why Distributed Exceptions Pattern?

**Decision**: Each package has its own `exceptions.py` with a hierarchy inheriting from core base exceptions.

**Rationale**:
- **Error Domain Isolation**: Exceptions are scoped to the package that raises them
- **Package Self-Containment**: Exception definitions travel with the code
- **Clear Hierarchy**: All exceptions inherit from `core.exceptions.TelemetryError` for system-wide catching
- **Specific Error Handling**: Consumers can catch package-specific exceptions for targeted recovery

**Exception Hierarchy Philosophy**:
```python
# Fine-grained catching (specific recovery)
except InvalidPayloadError:
    # Return 400 Bad Request to client

# Mid-level catching (package-specific recovery)
except IngestError:
    # Log and retry ingest operation

# Broad catching (system-wide error handling)
except TelemetryError:
    # Alert ops team, graceful degradation
```

**Alternative Considered**: All exceptions in core
- ❌ **Rejected**: Creates god-like exceptions file, couples services to each other's errors

**Trade-offs**:
- ✅ **Pro**: Package independence, fine-grained error handling, extraction-ready
- ⚠️ **Con**: More exception files to maintain

**Justification**: Error handling clarity and package independence justify the additional files.

---

### 5. Why Infrastructure as Reusable Libraries?

**Decision**: Stream, storage, alert, consumer, aggregation, and detection packages are designed as standalone infrastructure libraries.

**Rationale**:
- **Reusability**: Multiple services can use the same infrastructure without duplication
- **Testability**: Infrastructure can be tested independently of services
- **Swappability**: Redis can be replaced with Kafka by implementing the same protocol
- **Distribution**: Can be extracted to internal PyPI packages for organization-wide use

**Library Independence Philosophy**:
```python
# Consumers library: No infrastructure dependencies
# - Uses StreamProtocol (interface), not Redis (implementation)
# - Can consume from Redis, Kafka, RabbitMQ, SQS

# Aggregation library: No domain dependencies
# - Aggregates any numeric metrics
# - Works for telemetry, billing, analytics, fraud detection

# Detection library: No domain dependencies
# - Detects anomalies in any metric stream
# - Works for performance, security, fraud, quality monitoring
```

**Alternative Considered**: Embed infrastructure logic in services
- ❌ **Rejected**: Duplicates code across services, couples services to Redis, prevents reuse

**Trade-offs**:
- ✅ **Pro**: Reusability, testability, swappability, distribution
- ⚠️ **Con**: More packages to maintain and version

**Justification**: Reusability and flexibility far outweigh maintenance overhead.

---

### 6. Why Protocol-Driven Architecture?

**Decision**: Use Python protocols (PEP 544 structural typing) as primary contracts, supplemented by abstract base classes for shared implementation.

**Rationale**:

**Protocols Provide**:
1. **Structural Typing**: Classes implement protocols implicitly without inheritance ("duck typing")
2. **No Coupling**: Implementations don't need to inherit from a base class
3. **Easier Testing**: Mock objects automatically satisfy protocols
4. **Third-Party Integration**: External libraries can implement our protocols without modification
5. **Flexibility**: Multiple implementations can coexist without hierarchy conflicts

**Example - Protocol Contract**:
```python
# core/protocols.py - Pure contract definition
class StreamProtocol(Protocol):
    """Contract for stream operations."""
    async def publish(self, stream: str, data: dict) -> str: ...
    async def consume(self, stream: str, group: str) -> AsyncIterator[dict]: ...

# streams/redis_stream.py - Implicit satisfaction
class RedisStream:  # No inheritance required!
    async def publish(self, stream: str, data: dict) -> str:
        return await self._client.xadd(stream, data)
    
    async def consume(self, stream: str, group: str) -> AsyncIterator[dict]:
        async for message in self._client.xreadgroup(...):
            yield message

# Type checker validates: RedisStream satisfies StreamProtocol ✅
```

**Alternative Considered**: Pure abstract base classes (ABC)
- ❌ **Rejected**: Requires inheritance, couples implementations, harder to test with mocks

**Trade-offs**:
- ✅ **Pro**: Flexibility, no coupling, easy mocking, third-party integration
- ⚠️ **Con**: No runtime validation (only type-checker validation)
- ⚠️ **Con**: Less explicit for developers unfamiliar with protocols

**Justification**: Static type checking is sufficient, flexibility and testability are critical.

---

### 7. Why Hybrid Protocols + Abstract Base Classes?

**Decision**: Use protocols for contracts AND abstract base classes for shared implementation logic.

**Rationale**:

While protocols provide flexibility, ABCs enable code reuse when multiple implementations share common logic:
- **Protocols**: Define contracts for type checking and flexibility
- **ABCs**: Provide shared implementation (validation, logging, formatting)

**When to Use Each**:

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Protocol Only** | Varied implementations, minimal shared logic | `AlerterProtocol` (console, email, PagerDuty all different) |
| **Protocol + ABC** | Similar implementations with shared utilities | `StorageProtocol` + `BaseStorage` (all need key validation) |
| **ABC Only** | Strict inheritance, internal implementations | Rarely used in this codebase |

**Example - Storage with Shared Validation**:
```python
# core/protocols.py - Contract
class StorageProtocol(Protocol):
    async def store(self, key: str, value: Any) -> None: ...
    async def retrieve(self, key: str) -> Optional[Any]: ...

# storage/base.py - Shared implementation
class BaseStorage(ABC):
    """Shared validation and logging for all storage implementations."""
    
    def _validate_key(self, key: str) -> None:
        """Shared validation logic - no duplication."""
        if not key or not key.strip():
            raise ValueError("Storage key cannot be empty")
        if len(key) > 255:
            raise ValueError("Storage key too long")

# storage/redis_store.py - Concrete implementation
class RedisStore(BaseStorage):  # Inherits validation
    async def store(self, key: str, value: Any) -> None:
        self._validate_key(key)  # Use inherited validation
        await self._client.set(key, json.dumps(value))

# Type checker validates:
# ✅ RedisStore inherits BaseStorage (implementation reuse)
# ✅ RedisStore satisfies StorageProtocol (structural typing)
```

**Why Not Use ABCs Everywhere?**

Avoid pure ABC inheritance when:
1. **Implementations vary significantly**: Alert mechanisms have little shared logic
2. **Third-party integration**: External libraries can't inherit from our ABCs
3. **Maximum flexibility**: Protocols allow any implementation without coupling

**Trade-offs**:
- ✅ **Pro**: Contract flexibility + implementation efficiency
- ⚠️ **Con**: Two patterns to learn (protocols vs ABCs)

**Justification**: Hybrid approach provides both flexibility and code reuse without compromise.

---

### 8. Why Composition Over Inheritance?

**Decision**: Use constructor injection with protocol dependencies rather than inheritance hierarchies.

**Rationale**:
- **Testability**: Dependencies can be easily mocked in tests
- **Flexibility**: Different implementations can be swapped at runtime
- **Clarity**: Dependencies are explicit in the constructor signature
- **Loose Coupling**: Components depend on abstractions, not concretions
- **Avoids Fragile Base Class Problem**: Changes to base class don't break children

**Example - Worker Composition**:
```python
class TelemetryWorker:
    """Worker composes all dependencies - no inheritance."""
    
    def __init__(
        self,
        consumer: TelemetryConsumer,           # Injected
        aggregator: TumblingWindowAggregator,  # Injected
        detector: ThresholdDetector,           # Injected
        storage: StorageProtocol,              # Injected
        alerter: AlerterProtocol,              # Injected
    ) -> None:
        self._consumer = consumer
        self._aggregator = aggregator
        self._detector = detector
        self._storage = storage
        self._alerter = alerter
```

**Alternative Considered**: Inheritance-based architecture
- ❌ **Rejected**: Creates tight coupling, difficult testing, fragile base class problem

**Trade-offs**:
- ✅ **Pro**: Testability, flexibility, clarity, loose coupling
- ⚠️ **Con**: More verbose constructors (mitigated by dependency injection frameworks)

**Justification**: Testability and flexibility are critical for distributed systems.

---

### 9. Why Repository Extraction Strategy?

**Decision**: Design every package to be extracted into a separate repository with minimal refactoring.

**Rationale**:
- **Future Flexibility**: Organization grows, teams want independent repos
- **Reusability**: Infrastructure libraries can be shared organization-wide
- **Independent Evolution**: Libraries can be versioned and improved independently
- **Reduced Blast Radius**: Changes to one library don't break unrelated services

**Extraction Philosophy**:
```
Phase 1: Monorepo (current)    →  Phase 2: Extract libraries  →  Phase 3: Extract services
├── src/core/                       telemetry-core (PyPI)         telemetry-ingest (service)
├── src/streams/                    telemetry-streams (PyPI)      telemetry-processor (service)
├── src/storage/                    telemetry-storage (PyPI)
├── src/aggregation/                telemetry-aggregation (PyPI)
├── src/detection/                  telemetry-detection (PyPI)
├── src/ingest/                     telemetry-alerts (PyPI)
└── src/processor/                  telemetry-consumers (PyPI)
```

**Alternative Considered**: Design for monorepo only
- ❌ **Rejected**: Prevents future organizational growth, limits reusability

**Trade-offs**:
- ✅ **Pro**: Future flexibility, reusability, independent evolution
- ⚠️ **Con**: Requires discipline to maintain boundaries during development

**Justification**: Planning for growth is cheaper than refactoring later.

---

### 10. Why Layered Configuration Strategy?

**Decision**: Use Pydantic Settings with YAML files and environment variable overrides.

**Rationale**:
- **Type Safety**: Configuration is validated at startup with clear error messages
- **Flexibility**: YAML for complex settings, env vars for deployment-specific overrides
- **12-Factor Compliance**: Environment-based configuration for cloud deployments
- **Inheritance**: Shared settings in base class, service-specific settings in subclasses

**Configuration Priority (highest to lowest)**:
1. Environment variables (INGEST_API_PORT=9000)
2. .env file
3. YAML config file
4. Default values in code

**Alternative Considered**: Hardcoded configuration
- ❌ **Rejected**: Inflexible, requires code changes for configuration updates

**Trade-offs**:
- ✅ **Pro**: Type safety, flexibility, 12-factor compliance
- ⚠️ **Con**: Requires Pydantic dependency (already required by FastAPI)

**Justification**: Type-safe configuration prevents entire class of runtime errors.

---

### 11. Why Async/Await Throughout?

**Decision**: Use async/await for all I/O operations (HTTP, Redis, stream processing).

**Rationale**:
- **Performance**: Non-blocking I/O enables high concurrency (handle 1000s of requests with single process)
- **Scalability**: Single worker can process many concurrent streams
- **Modern Python**: Leverages Python 3.10+ async capabilities
- **Framework Alignment**: FastAPI and Redis async client are async-native

**Alternative Considered**: Synchronous with threading
- ❌ **Rejected**: Higher memory overhead, GIL contention, complex synchronization

**Trade-offs**:
- ✅ **Pro**: High concurrency, resource efficiency, modern Python
- ⚠️ **Con**: Async propagates through call stack (all callers must be async)

**Justification**: Async is standard for modern Python I/O-bound applications.

---

### 12. Why Structured Logging?

**Decision**: Use structured logging with standard library logging, formatted with key-value pairs.

**Rationale**:
- **Observability**: Logs are queryable in log aggregation systems (Splunk, Datadog, ELK)
- **Context**: Rich context attached to log entries (device_id, metric_name, correlation_id)
- **Debugging**: Easy to filter and search logs programmatically

**Logging Pattern**:
```python
import logging as _log

_log.info(
    "Processing telemetry event: device_id=%s, metric=%s, value=%f",
    event.device_id,
    event.metric_name,
    event.metric_value,
)
```

**Alternative Considered**: f-string logging
- ❌ **Rejected**: Harder to parse, no structured querying

**Justification**: Observability is critical for distributed systems.

---

## Trade-Offs Summary

| Decision | Alternative | Chosen Because | Trade-off Accepted |
|----------|-------------|----------------|-------------------|
| **Protocols** | ABCs | Flexibility, testability | No runtime validation |
| **Distributed Models** | Central models | Self-containment | More files |
| **Monorepo** | Multi-repo | Development velocity | Initial coupling |
| **Redis Streams** | Kafka | Simpler deployment | Less mature at scale |
| **Composition** | Inheritance | Testability | Verbose constructors |
| **Async** | Sync + Threading | Resource efficiency | Async propagation |
| **Pydantic Config** | Plain dicts | Type safety | Requires dependency |

---

## Design Patterns Applied

1. **Protocol-Driven Design**: Services depend on abstractions (protocols), not implementations
2. **Composition Over Inheritance**: Dependencies injected, not inherited
3. **Distributed Domain Models**: Each package owns its models
4. **Hybrid Protocol + ABC**: Contracts via protocols, utilities via ABCs
5. **Repository Extraction Pattern**: Packages designed to become standalone
6. **Layered Configuration**: Base config + service overrides + environment variables
7. **Consumer Group Pattern**: Distributed processing with automatic load balancing
8. **At-Least-Once Delivery**: Messages acknowledged after processing, automatic retry

---

## Validation Checklist

✅ **SOLID Principles Applied**
- Single Responsibility: Each module has one clear purpose
- Open/Closed: Extensible via protocols without modifying core
- Liskov Substitution: All protocol implementations are interchangeable
- Interface Segregation: Focused protocols
- Dependency Inversion: Depend on protocols, not classes

✅ **DRY Compliance**
- No duplicated logic across services
- Shared abstractions in core
- Reusable libraries

✅ **Type Safety**
- Full type annotations (mypy strict)
- py.typed markers
- Pydantic for configuration

✅ **Testability**
- All dependencies injected
- Easy mocking
- Tests mirror source

✅ **Future-Proof**
- Extraction-ready
- Clear boundaries
- Type information travels with code

---

## Conclusion

This design balances immediate implementation needs with long-term maintainability. Every decision prioritizes:

1. **Developer Experience**: Clear structure, type safety, easy testing
2. **Maintainability**: Self-documenting, clear boundaries
3. **Scalability**: Protocol-driven, extraction-ready, loose coupling
4. **Quality**: Type checking, test coverage, defensive programming

All decisions documented here can be traced to specific trade-offs and business value.

**For system structure, component details, and operational instructions, see:** [ARCHITECTURE.md](ARCHITECTURE.md)
