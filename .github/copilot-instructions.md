---
applyTo: '**'
---

# GitHub Copilot Python Coding Standards

## Core Principles
- Write Pythonic, idiomatic code following DRY and SOLID principles
- Use strong typing, defensive programming, and meaningful logging
- Prioritize readability, modularity, efficiency and testability
- Use `import logging as _log` for module-level logging
- Always assign variables before returning (no direct expression returns)
- **Favor composition over inheritance** - inject dependencies, use delegation patterns, compose behavior from smaller components

## Coding Patterns
- Class-level type annotations for instance variables
- Use `Optional` for nullable variables, `or`/`and` operators when logical
- Prefer `if not x:` over `if x is False:`, use `any()`/`all()` for collections
- Pseudo-private methods with `_` prefix for internal logic separation
- Properties for defensive programming, `validate()` methods that raise, `is_valid()` methods that return booleans
- Use `with suppress(Exception):` for non-critical exception handling
- NamedTuple for simple containers, dataclass for complex structures
- Enums for constants, ABCs for interfaces, Protocols for structural typing
-  catch specific exceptions with `from` for chaining
- Create `__repr__` methods where appropriate
- assign to a self documenting variable before returning from functions/methods
- before raising an exception, log the error message.
- Never use f strings for log messages, always use %s formatting with variables passed as arguments to the log method.
- Use `__slots__` in classes where appropriate to reduce memory overhead (most of the time)

## Data Structure Selection
- **Sets** for membership checks (`item in my_set`) and unique collections
- **Lists** for ordered, mutable sequences when you need to append/extend
- **Deques** from collections for efficient operations at both ends
- **Tuples** for immutable sequences and multiple return values
- **Dictionaries** for key-value mappings and fast lookups
- **NamedTuples** for simple immutable containers with named fields
- **Dataclasses** for more complex structured data. Use kw_only=True, frozen=True, and slots=True when appropriate (most of the time)

### Advanced Collections
- `frozenset` for immutable sets
- `OrderedDict` when insertion order matters (pre-Python 3.7)
- `defaultdict` and `Counter` from collections when appropriate
- `heapq` for priority queues
- `bisect` for maintaining sorted sequences

### Threading
If there is method or function that will take in a large number of items to process, use map to begin with. If there is a prompted need to be explicit about threading use threading pool as follows and replace `map`:

```python
from multiprocessing.pool import ThreadPool as Pool
THREADS = 1 # adjust based on expected workload

pool = Pool(THREADS)
thread_map = pool.imap  # or pool.map_unordered
```

## Quality Requirements

### Testing
Use pytest (check dev dependencies, default if not specified). 100% coverage including happy paths, edge cases, validation, exceptions

**Test Organization:**
- All tests in `tests/` directory
- Test files named `test_<module_name>.py` (e.g., `test_user.py` for `user.py`)
- Test classes named `TestClassName` for each class being tested
- Group related tests within the appropriate test class
- Use `@pytest.mark.parametrize` for testing multiple input combinations
- Leverage pytest fixtures for setup/teardown and reusable test data
- Mock external connections, APIs, and dependencies using `unittest.mock` or `pytest-mock`

### Linting
Check dev dependencies for available tools. Defaults: ruff for linting, mypy for type checking, pylint as fallback. Must pass all configured linters with no errors

### Documentation
**Docstrings**: PEP 257 compliant, Google-style for all modules/classes/functions/methods. 72 chars line limit. Must include:
- **Module-level**: Purpose, main classes/functions, usage overview, examples when appropriate
- **Class-level**: Purpose, key attributes, usage patterns, examples when appropriate  
- **Function/Method-level**: Clear description, Args, Returns, Raises, Examples when helpful

**Project Documentation**: Update README.md or relevant docs with new features, usage examples, configuration options, and any breaking changes only when necessary.

### Type Checking
Full annotations with mypy strict mode, avoid `Any`, use `Optional`, `Union`, `Literal` as needed

## Example: Complete Implementation Following All Standards

```python
"""Alert endpoint implementation for Funnel API.

This module provides the AlertEndpoint class for submitting alerts to external
monitoring systems. It demonstrates proper Python coding standards including
strong typing, defensive programming, and comprehensive error handling.

Classes:
    AlertEndpoint: Main endpoint class for alert submission
    AlertSeverity: Enum defining valid alert severity levels
    AlertConfig: Configuration dataclass for endpoint settings

Example:
    Basic alert submission::

        config = AlertConfig(url="https://api.example.com", timeout=30)
        endpoint = AlertEndpoint(config, auth_token="secret")
        
        success = endpoint.submit_alert(
            ci_name="web-server-01",
            severity=AlertSeverity.HIGH,
            message="CPU usage above 90%"
        )
"""
import logging
from contextlib import suppress
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union
from collections.abc import Callable

_log = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, kw_only=True, slots=True)
class AlertConfig:
    """Configuration for alert endpoint.
    
    Attributes:
        url: Base URL for the alert API
        timeout: Request timeout in seconds
        retry_count: Number of retry attempts on failure
        validate_ssl: Whether to validate SSL certificates
    """
    
    url: str
    timeout: int = 30
    retry_count: int = 3
    validate_ssl: bool = True
    
    def is_valid(self) -> bool:
        """Check if configuration is valid without raising.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        has_url = bool(self.url and self.url.strip())
        timeout_positive = self.timeout > 0
        retry_non_negative = self.retry_count >= 0
        
        is_valid_config = has_url and timeout_positive and retry_non_negative
        return is_valid_config
    
    def validate(self) -> None:
        """Validate configuration and raise if invalid.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.is_valid():
            error_message = "Invalid configuration: url=%s, timeout=%d, retry_count=%d"
            _log.error(error_message, self.url, self.timeout, self.retry_count)
            raise ValueError("Invalid AlertConfig") from None


class AlertEndpoint:
    """Endpoint for submitting alerts to external monitoring systems.
    
    This class handles alert submission with retry logic, validation, and
    comprehensive error handling. It uses composition to inject dependencies
    and follows defensive programming practices.
    
    Attributes:
        _config: Endpoint configuration
        _auth_token: Authentication token for API requests
        _transport: Optional transport layer for HTTP requests
        _retry_strategy: Optional custom retry strategy
    
    Example:
        Submit an alert with custom configuration::
        
            config = AlertConfig(url="https://alerts.example.com", timeout=60)
            endpoint = AlertEndpoint(config, auth_token="abc123")
            
            result = endpoint.submit_alert(
                ci_name="db-prod-01",
                severity=AlertSeverity.CRITICAL,
                message="Database connection pool exhausted"
            )
    """
    __slots__ = (
        "_config",
        "_auth_token",
        "_transport",
        "_retry_strategy",
    )
    _config: AlertConfig
    _auth_token: str
    _transport: Optional[object]
    _retry_strategy: Optional[Callable[[int], bool]]
    
    def __init__(
        self,
        config: AlertConfig,
        auth_token: str,
        transport: Optional[object] = None,
        retry_strategy: Optional[Callable[[int], bool]] = None
    ) -> None:
        """Initialize the alert endpoint.
        
        Args:
            config: Endpoint configuration
            auth_token: Authentication token for API requests
            transport: Optional HTTP transport layer (injected dependency)
            retry_strategy: Optional custom retry strategy function
            
        Raises:
            ValueError: If config is invalid or auth_token is empty
        """
        config.validate()
        
        if not auth_token or not auth_token.strip():
            error_message = "auth_token cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None
        
        self._config = config
        self._auth_token = auth_token
        self._transport = transport
        self._retry_strategy = retry_strategy or self._default_retry_strategy
        
        _log.info("AlertEndpoint initialized with url=%s", config.url)
    
    def __repr__(self) -> str:
        """Return string representation of endpoint.
        
        Returns:
            String representation showing key attributes
        """
        representation = (
            f"AlertEndpoint(url={self._config.url!r}, "
            f"timeout={self._config.timeout}, "
            f"retry_count={self._config.retry_count})"
        )
        return representation
    
    @property
    def config(self) -> AlertConfig:
        """Get endpoint configuration (defensive copy).
        
        Returns:
            Frozen copy of configuration
        """
        return self._config
    
    def submit_alert(
        self,
        *,
        ci_name: str,
        severity: AlertSeverity,
        message: str,
        source_id: Optional[str] = None
    ) -> bool:
        """Submit an alert to the monitoring system.
        
        Args:
            ci_name: Configuration item name (target system identifier)
            severity: Alert severity level
            message: Human-readable alert description
            source_id: Optional unique alert identifier
            
        Returns:
            True if alert was submitted successfully, False otherwise
            
        Raises:
            ValueError: If ci_name or message is empty
            RuntimeError: If submission fails after all retries
            
        Example:
            Submit a critical alert::
            
                success = endpoint.submit_alert(
                    ci_name="web-01",
                    severity=AlertSeverity.CRITICAL,
                    message="Service unavailable"
                )
        """
        self._validate_alert_params(ci_name, message)
        
        payload = self._build_payload(ci_name, severity, message, source_id)
        
        submission_successful = self._send_with_retry(payload)
        return submission_successful
    
    def _validate_alert_params(self, ci_name: str, message: str) -> None:
        """Validate alert parameters.
        
        Args:
            ci_name: Configuration item name
            message: Alert message
            
        Raises:
            ValueError: If parameters are invalid
        """
        validation_errors = []
        
        if not ci_name or not ci_name.strip():
            validation_errors.append("ci_name cannot be empty")
        
        if not message or not message.strip():
            validation_errors.append("message cannot be empty")
        
        if validation_errors:
            error_message = "Validation failed: %s"
            _log.error(error_message, ", ".join(validation_errors))
            raise ValueError("; ".join(validation_errors)) from None
    
    def _build_payload(
        self,
        ci_name: str,
        severity: AlertSeverity,
        message: str,
        source_id: Optional[str]
    ) -> dict[str, Union[str, None]]:
        """Build alert payload for API submission.
        
        Args:
            ci_name: Configuration item name
            severity: Alert severity
            message: Alert message
            source_id: Optional source identifier
            
        Returns:
            Dictionary containing alert payload
        """
        payload = {
            "ci_name": ci_name.strip(),
            "severity": severity.value,
            "message": message.strip(),
            "source_id": source_id
        }
        
        _log.debug("Built payload for ci_name=%s, severity=%s", ci_name, severity.value)
        return payload
    
    def _send_with_retry(self, payload: dict[str, Union[str, None]]) -> bool:
        """Send alert with retry logic.
        
        Args:
            payload: Alert payload to send
            
        Returns:
            True if sent successfully, False otherwise
            
        Raises:
            RuntimeError: If all retry attempts fail
        """
        for attempt in range(self._config.retry_count + 1):
            with suppress(ConnectionError, TimeoutError):
                result = self._send_alert(payload)
                
                if result:
                    _log.info("Alert sent successfully on attempt %d", attempt + 1)
                    return True
            
            should_retry = self._retry_strategy(attempt)
            if not should_retry:
                break
            
            _log.warning("Retry attempt %d failed for alert", attempt + 1)
        
        error_message = "Failed to send alert after %d attempts"
        _log.error(error_message, self._config.retry_count + 1)
        raise RuntimeError("Alert submission failed after all retries") from None
    
    def _send_alert(self, payload: dict[str, Union[str, None]]) -> bool:
        """Send alert using transport layer.
        
        Args:
            payload: Alert payload
            
        Returns:
            True if successful, False otherwise
        """
        if not self._transport:
            _log.debug("No transport configured, simulating successful send")
            send_successful = True
            return send_successful
        
        # Actual transport implementation would go here
        send_successful = True
        return send_successful
    
    @staticmethod
    def _default_retry_strategy(attempt: int) -> bool:
        """Default retry strategy.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            True if should retry, False otherwise
        """
        max_attempts = 3
        should_retry = attempt < max_attempts
        return should_retry


__all__ = [
    "AlertEndpoint",
    "AlertSeverity",
    "AlertConfig",
]
```
