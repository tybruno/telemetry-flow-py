"""Edge case tests for MessageDeserializer."""

import pytest

from src.consumers.deserializer import MessageDeserializer
from src.consumers.exceptions import DeserializationError


class TestMessageDeserializerEdgeCases:
    """Test edge cases for MessageDeserializer."""

    @pytest.fixture
    def deserializer(self) -> MessageDeserializer:
        """Create deserializer instance.

        Returns:
            MessageDeserializer instance.
        """
        return MessageDeserializer()

    def test_deserialize_with_generic_exception(
        self,
        deserializer: MessageDeserializer,
    ) -> None:
        """Test deserializer wraps generic exceptions.

        Args:
            deserializer: MessageDeserializer fixture.
        """
        # Invalid JSON that will cause json.loads to raise
        invalid_message = b"not valid json at all"

        with pytest.raises(DeserializationError, match="Failed to deserialize message"):
            deserializer.deserialize(invalid_message)


__all__: list[str] = []
