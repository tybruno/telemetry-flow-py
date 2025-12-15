"""Tests for core configuration."""

import os
from unittest.mock import patch

import pytest

from src.core.config import BaseConfig


class TestBaseConfig:
    """Test suite for BaseConfig class."""

    def test_base_config_defaults(self) -> None:
        """Test BaseConfig has reasonable defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = BaseConfig()

            assert config.redis_url == "redis://localhost:6379"
            assert config.log_level == "INFO"
            assert config.environment == "development"

    def test_base_config_from_environment(self) -> None:
        """Test BaseConfig loads from environment variables."""
        env_vars = {
            "REDIS_URL": "redis://prod-redis:6379",
            "LOG_LEVEL": "ERROR",
            "ENVIRONMENT": "production",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = BaseConfig()

            assert config.redis_url == "redis://prod-redis:6379"
            assert config.log_level == "ERROR"
            assert config.environment == "production"

    @pytest.mark.parametrize(
        "log_level",
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    def test_base_config_valid_log_levels(self, log_level: str) -> None:
        """Test BaseConfig accepts valid log levels.

        Args:
            log_level: Valid log level string.
        """
        env_vars = {"LOG_LEVEL": log_level}

        with patch.dict(os.environ, env_vars, clear=True):
            config = BaseConfig()
            assert config.log_level == log_level

    @pytest.mark.parametrize(
        "environment",
        ["development", "staging", "production"],
    )
    def test_base_config_valid_environments(self, environment: str) -> None:
        """Test BaseConfig accepts valid environments.

        Args:
            environment: Valid environment string.
        """
        env_vars = {"ENVIRONMENT": environment}

        with patch.dict(os.environ, env_vars, clear=True):
            config = BaseConfig()
            assert config.environment == environment

    def test_base_config_redis_url_variations(self) -> None:
        """Test various Redis URL formats."""
        redis_urls = [
            "redis://localhost:6379",
            "redis://user:pass@host:6379",
            "redis://host:6379/0",
            "rediss://secure-host:6380",
        ]

        for url in redis_urls:
            with patch.dict(os.environ, {"REDIS_URL": url}, clear=True):
                config = BaseConfig()
                assert config.redis_url == url

    def test_base_config_is_pydantic_settings(self) -> None:
        """Test BaseConfig is a Pydantic BaseSettings."""
        config = BaseConfig()
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")

    def test_base_config_can_be_dumped(self) -> None:
        """Test BaseConfig can be dumped to dict."""
        config = BaseConfig()
        config_dict = config.model_dump()

        assert isinstance(config_dict, dict)
        assert "redis_url" in config_dict
        assert "log_level" in config_dict
        assert "environment" in config_dict


__all__: list[str] = []
