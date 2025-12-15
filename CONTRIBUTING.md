# Contributing Guide

This document outlines development practices, code quality standards, and testing requirements for the telemetry-flow-py project.

---

## Development Setup

### Prerequisites

- **Python 3.10+**: For local development
- **Docker & Docker Compose**: For containerized services and integration testing
- **Redis**: Included in Docker Compose, or install locally for development

### Local Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install core dependencies
pip install -e .

# Install with development dependencies (recommended)
pip install -e ".[dev]"

# Or use Makefile
make install-dev
```

### Quick Verification

```bash
# Run all checks
make check

# Run all tests
make test

# Or with coverage
make test-cov
```

---

## Code Quality Standards

This project follows strict code quality standards defined in [`.github/copilot-instructions.md`](.github/copilot-instructions.md).

### Core Principles

- **Pythonic Code**: Write idiomatic Python following PEP 8 and DRY principles
- **Strong Typing**: Full type annotations with mypy strict mode enabled
- **Defensive Programming**: Validate inputs, use `Optional` for nullable values
- **Error Handling**: Log errors before raising exceptions with context
- **Composition Over Inheritance**: Inject dependencies, use delegation patterns
- **Meaningful Logging**: Use structured logging with proper log levels

### Code Patterns

```python
# ✅ Good: Type hints, validation, proper logging
import logging as _log
from typing import Optional

_log = logging.getLogger(__name__)

class DataProcessor:
    __slots__ = ("_cache", "_timeout")
    
    def __init__(self, timeout: int):
        if timeout <= 0:
            error_message = "Timeout must be positive"
            _log.error(error_message)
            raise ValueError(error_message)
        self._timeout = timeout

    def process(self, data: dict[str, str]) -> Optional[str]:
        """Process data with error handling.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Processed result or None if processing failed
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            error_message = "Data cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message)
        
        # Implementation...
        return result

# ❌ Bad: No types, no validation, no logging
def process_data(data):
    return transform(data)
```

### Type Checking

Use full type annotations and enable mypy strict mode:

```bash
# Type check the entire project
make typecheck

# Or with mypy directly
mypy src/ --strict
```

### Data Structure Selection

- **Sets** for membership checks and unique collections
- **Lists** for ordered, mutable sequences
- **Tuples** for immutable sequences and return values
- **Dictionaries** for key-value mappings
- **NamedTuples** for simple immutable containers
- **Dataclasses** for complex structured data (with `kw_only=True`, `frozen=True`, `slots=True`)

---

## Testing Requirements

### Test Coverage Goals

- **Overall Target**: 95%+ code coverage
- **Core Modules**: 100% coverage for critical paths
- **Integration Tests**: Cover critical service interactions
- **100% Test Pass Rate**: All tests must pass before merging

### Test Organization

Tests are organized by module in the `tests/` directory:

```
tests/
├── aggregation/          # Aggregation module tests
├── alerts/              # Alert system tests
├── consumers/           # Stream consumer tests
├── detection/           # Anomaly detection tests
├── ingest/             # Ingest service tests
├── processor/          # Processor worker tests
├── streams/            # Stream protocol tests
└── storage/            # Storage layer tests
```

### Test File Naming

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<behavior>`

```python
# ✅ Good test naming
class TestStreamConsumer:
    def test_consume_messages_success(self):
        """Test consumer successfully consumes messages."""
        # ...
    
    def test_consume_empty_stream_raises(self):
        """Test consume raises ValueError with empty stream."""
        # ...
```

### Writing Tests

#### Unit Tests

```python
"""Tests for processor worker."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.processor.worker import TelemetryWorker

class TestTelemetryWorker:
    """Tests for TelemetryWorker class."""
    
    @pytest.fixture
    def mock_stream(self):
        """Create mock stream."""
        return MagicMock()
    
    @pytest.mark.asyncio
    async def test_process_metrics_success(self, mock_stream):
        """Test worker successfully processes metrics."""
        worker = TelemetryWorker(stream=mock_stream)
        
        # Execute
        result = await worker.process_metric(device_id="router-01", value=95.5)
        
        # Assert
        assert result is not None
        mock_stream.publish.assert_called_once()
```

#### Integration Tests

```python
@pytest.mark.integration
class TestProcessorIntegration:
    """Integration tests for processor worker with Redis."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_processing(self, redis_client):
        """Test complete processing pipeline."""
        # Uses real Redis instance
        # Requires Docker/Redis to be running
        # ...
```

### Running Tests

```bash
# Run all tests (unit + integration)
make test

# Run unit tests only (fast, no Docker required)
make test-unit

# Run specific test file
pytest tests/aggregation/test_tumbling_window.py -v

# Run tests matching pattern
pytest tests/ -k "window" -v

# Run with coverage
make test-cov

# Generate HTML coverage report
make test-cov-html
# Open htmlcov/index.html in browser

# Run only integration tests
pytest -m integration -v

# Exclude integration tests
pytest -m "not integration" -v
```

### Test Markers

```python
# Mark integration tests that require Docker/Redis
@pytest.mark.integration
async def test_redis_integration():
    # ...

# Mark slow tests
@pytest.mark.slow
def test_complex_operation():
    # ...
```

### Mocking Strategies

```python
from unittest.mock import AsyncMock, MagicMock, patch

# Mock async functions
async_mock = AsyncMock(return_value="result")

# Mock regular functions with specific side effects
mock_func = MagicMock(side_effect=Exception("Error"))

# Patch imported modules
with patch("src.module.function") as mock_func:
    # Test code
    mock_func.assert_called_once_with(expected_arg)
```

---

## Linting & Formatting

### Ruff Linter

```bash
# Check code with ruff
make lint

# Auto-fix linting issues
make fix

# Check formatting only
make format
```

### Line Length

- **Python**: 100 characters (configured in `pyproject.toml`)
- **Docstrings**: 72 characters

### Import Organization

Imports should follow this order:
1. Standard library imports
2. Third-party imports
3. Local imports

```python
import logging
from typing import Optional

import redis.asyncio as redis
import pytest

from src.streams.redis_stream import RedisStream
from src.streams.exceptions import StreamError
```

---

## Documentation

### Docstring Standards

All modules, classes, functions, and methods must include docstrings following PEP 257 and Google style:

```python
"""Module-level docstring.

Describe the module's purpose, key classes, and usage examples.

Example:
    Basic usage example::

        from src.module import MyClass
        
        instance = MyClass(config)
        result = instance.process(data)
"""

class MyClass:
    """Class-level docstring.
    
    Describe purpose, attributes, and usage patterns.
    
    Attributes:
        param1: Description of param1
        param2: Description of param2
    
    Example:
        Usage example::
        
            instance = MyClass(param1, param2)
            instance.do_something()
    """
    
    def method(self, arg1: str, arg2: int) -> bool:
        """Method-level docstring.
        
        Clear description of what the method does.
        
        Args:
            arg1: Description of arg1
            arg2: Description of arg2
        
        Returns:
            Description of return value
        
        Raises:
            ValueError: Description of when raised
            RuntimeError: Description of when raised
        
        Example:
            Usage example::
            
                result = instance.method("value", 42)
        """
        # Implementation...
        return result
```

### Line Limits

- **Docstring lines**: 72 characters maximum
- **Code lines**: 100 characters maximum
- **Comments**: Follow docstring line limits

---

## Adding New Features

### Development Workflow

1. **Create an issue** describing the feature or bug
2. **Write tests first** (TDD approach)
   - Write failing tests for the desired behavior
   - Run tests to confirm they fail
3. **Implement feature** following existing patterns
   - Follow code quality standards
   - Include proper docstrings
   - Add type annotations
4. **Verify all checks pass**
   ```bash
   make check && make test-cov
   ```
5. **Update documentation**
   - Update docstrings
   - Update README if user-facing
   - Update ARCHITECTURE.md if design changes
6. **Commit with descriptive message**
   ```bash
   git commit -m "feat: add feature description
   
   - Detailed explanation of changes
   - Tests added for feature
   - Any breaking changes noted"
   ```

### Commit Message Format

Follow conventional commits:

```
<type>: <short description (50 chars max)>

<optional detailed body (72 chars per line)>

<optional footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `test`: Test improvements
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Build, dependencies, etc.

**Examples**:
```
feat: add consumer group error handling

- Handle NOGROUP errors with ConsumerGroupError
- Add tests for error scenarios
- Update documentation

Closes #42
```

---

## Makefile Reference

### Installation

```bash
make install              # Install production dependencies
make install-dev         # Install development dependencies
```

### Testing

```bash
make test                      # Run all tests
make test-unit                 # Unit tests only
make test-integration          # Integration tests only
make test-cov                  # Tests with coverage report
make test-integration-cov      # Integration tests with coverage
make test-cov-html             # Generate HTML coverage report
```

### Code Quality

```bash
make lint                 # Check code with ruff linter
make format              # Check code formatting
make fix                 # Auto-fix linting and formatting
make typecheck           # Run mypy type checker
make check               # Run all checks (lint + format + typecheck)
```

### Docker

```bash
make docker-up           # Start all services (Redis, etc.)
make docker-down         # Stop and remove services
make docker-logs         # View service logs
make docker-restart      # Restart all services
make docker-clean        # Stop services and remove volumes
```

### Combined

```bash
make all                 # Run all checks and tests
make clean              # Remove build artifacts
```

---

## Python Version Support

The project supports Python 3.10+. Ensure compatibility:

```bash
# Test with specific Python version
python3.10 -m pytest tests/

# Or use pyenv to manage versions
pyenv install 3.10.0 3.11.0 3.12.0
pyenv local 3.10.0
python -m pytest tests/
```

---

## Release & Deployment

### Version Management

This project uses semantic versioning (MAJOR.MINOR.PATCH):

```bash
# Create release tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

### Automated Publishing

Releases are automatically published to PyPI via GitHub Actions when a release tag is created.

**Publication Process**:
1. Create a release on GitHub with version tag
2. GitHub Actions automatically builds distributions
3. Package is published to PyPI using OIDC trusted publishing

**For detailed CI/CD configuration, see:** [docs/METHODOLOGY.md](docs/METHODOLOGY.md#phase-4-development-infrastructure)

---

## Troubleshooting

### Common Issues

**Q: Tests fail with "Cannot connect to Redis"**
```bash
# Start Redis in Docker
make docker-up

# Then run tests
make test-integration
```

**Q: Mypy complains about missing types**
- Run `make typecheck` to see full report
- Add missing type annotations
- Use `# type: ignore` only as last resort with comment

**Q: Ruff formatting conflicts**
```bash
# Auto-fix all issues
make fix

# Then verify with check
make check
```

**Q: Import errors in tests**
```bash
# Ensure development dependencies installed
make install-dev

# Reinstall editable package
pip install -e ".[dev]"
```

---

## Getting Help

- **Documentation**: See [docs/](docs/) for comprehensive documentation
- **Issues**: Create an issue describing the problem
- **Code Review**: Request review in PR for architectural questions

---

## Resources

- **Python Style Guide**: [PEP 8](https://pep8.org/)
- **Type Hints**: [PEP 484](https://peps.python.org/pep-0484/)
- **Docstring Format**: [PEP 257](https://peps.python.org/pep-0257/)
- **Pytest Documentation**: [pytest.org](https://docs.pytest.org/)
- **Ruff Documentation**: [github.com/astral-sh/ruff](https://github.com/astral-sh/ruff)
- **Mypy Documentation**: [mypy.readthedocs.io](https://mypy.readthedocs.io/)
