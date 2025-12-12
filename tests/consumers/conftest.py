"""Consumer library test fixtures.

Provides test fixtures specific to consumer library testing including
mock streams, sample messages, and consumer configurations.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.core.protocols import StreamProtocol


@pytest.fixture
def mock_stream() -> Mock:
    """Mock StreamProtocol implementation for testing.
    
    Returns:
        Mock stream with async methods configured
        
    Example:
        async def test_consumer(mock_stream):
            consumer = StreamConsumer(stream=mock_stream, ...)
            mock_stream.consume.return_value = [sample_message]
    """
    stream = Mock(spec=StreamProtocol)
    stream.consume = AsyncMock(return_value=[])
    stream.acknowledge = AsyncMock()
    stream.create_consumer_group = AsyncMock()
    return stream


@pytest.fixture
def sample_message_data() -> dict:
    """Sample raw message data for testing deserialization.
    
    Returns:
        Dictionary representing raw stream message
        
    Example:
        def test_deserialize(sample_message_data):
            event = deserializer.deserialize(sample_message_data)
            assert event.device_id == "router-01"
    """
    raise NotImplementedError


@pytest.fixture
def consumer_config() -> dict:
    """Standard consumer configuration for testing.
    
    Returns:
        Dictionary with consumer configuration values
        
    Example:
        def test_consumer_init(consumer_config):
            consumer = StreamConsumer(**consumer_config)
            assert consumer.stream_name == "test-stream"
    """
    raise NotImplementedError
