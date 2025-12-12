"""Base configuration classes for all services.

This module provides the base configuration class that all service-specific
configurations inherit from. Uses Pydantic Settings for type-safe
configuration with environment variable support.

Classes:
    BaseConfig: Base configuration with shared settings.

Example:
    Creating a service-specific configuration::
    
        from src.core.config import BaseConfig
        
        class IngestConfig(BaseConfig):
            api_host: str = "0.0.0.0"
            api_port: int = 8000
            
            class Config:
                env_prefix = "INGEST_"
        
        # Load configuration
        config = IngestConfig()
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Base configuration for all services.
    
    Provides shared configuration settings that all services need,
    including Redis connection, logging, and environment settings.
    Service-specific configs inherit from this class.
    
    Attributes:
        redis_url: Redis connection URL.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        environment: Deployment environment (development, staging, production).
    
    Example:
        Loading configuration with env vars::
        
            # Set: REDIS_URL=redis://localhost:6379
            config = BaseConfig()
            print(config.redis_url)  # redis://localhost:6379
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for streams and state storage",
    )
    
    log_level: str = Field(
        default="INFO",
        description="Logging level for the service",
    )
    
    environment: str = Field(
        default="development",
        description="Deployment environment (development, staging, production)",
    )


__all__ = [
    "BaseConfig",
]
