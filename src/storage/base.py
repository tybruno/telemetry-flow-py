"""Base storage implementation with shared utilities.

This module provides an abstract base class for storage implementations,
offering shared validation and logging functionality while allowing concrete
classes to implement protocol-specific methods.

Classes:
    BaseStorage: Abstract base class for storage implementations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

_log = logging.getLogger(__name__)


class BaseStorage(ABC):
    """Abstract base class for storage implementations.
    
    Provides shared validation and logging utilities for all storage
    implementations while enforcing core storage operations through
    abstract methods. Concrete classes inherit from this base and also
    satisfy the StorageProtocol contract.
    
    This hybrid approach combines:
    - Protocol: Defines contract for duck typing and flexibility
    - ABC: Provides shared implementation for common operations
    
    Attributes:
        _connection: Internal connection object to storage backend.
    
    Example:
        class RedisStore(BaseStorage):
            async def store(self, key: str, value: Any) -> None:
                self._validate_key(key)
                self._log_operation("store", key)
                # Redis-specific implementation
                raise NotImplementedError
    """
    
    _connection: Optional[object]
    
    def __init__(self, connection: Optional[object] = None) -> None:
        """Initialize base storage with optional connection.
        
        Args:
            connection: Optional connection object to storage backend.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def store(self, key: str, value: Any) -> None:
        """Store a value with the given key.
        
        Must be implemented by concrete classes to handle storage-specific
        persistence logic.
        
        Args:
            key: Storage key identifier.
            value: Value to store (will be serialized).
            
        Raises:
            ValueError: If key is invalid.
            StorageError: If storage operation fails.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key.
        
        Must be implemented by concrete classes to handle storage-specific
        retrieval logic.
        
        Args:
            key: Storage key identifier.
            
        Returns:
            Retrieved value or None if not found.
            
        Raises:
            ValueError: If key is invalid.
            StorageError: If retrieval operation fails.
        """
        raise NotImplementedError
    
    def _validate_key(self, key: str) -> None:
        """Validate storage key format.
        
        Shared validation logic used by all storage implementations.
        Ensures keys are non-empty and contain valid characters.
        
        Args:
            key: Key to validate.
            
        Raises:
            ValueError: If key is empty or contains invalid characters.
            
        Example:
            self._validate_key(key)  # Before storing
        """
        raise NotImplementedError
    
    def _log_operation(self, operation: str, key: str) -> None:
        """Log storage operation for debugging and monitoring.
        
        Shared logging utility used by all storage implementations.
        Provides consistent logging format across storage backends.
        
        Args:
            operation: Operation name (e.g., "store", "retrieve").
            key: Storage key being operated on.
            
        Example:
            self._log_operation("store", key)
        """
        raise NotImplementedError


__all__ = ["BaseStorage"]
