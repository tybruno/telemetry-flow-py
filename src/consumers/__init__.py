"""Reusable stream consumer infrastructure library.

This library provides generic stream consumption capabilities with robust
error handling, message processing, and backpressure management. It can be
used by any service that needs to consume messages from streaming platforms.

Classes:
    StreamConsumer: Generic stream consumer with composition pattern
    MessageDeserializer: Message parsing and validation
    ConsumerErrorHandler: Exponential backoff retry logic
    BackpressureManager: Rate limiting and backpressure management

Example:
    Basic consumer setup::

        from consumers import StreamConsumer
        from core.protocols import StreamProtocol

        consumer = StreamConsumer(
            stream=stream_implementation,
            deserializer=deserializer,
            error_handler=error_handler,
            backpressure=backpressure_manager,
            stream_name="events",
            group_name="processors",
            consumer_name="worker-01"
        )

        async for message in consumer.consume():
            # Process message
            await consumer.acknowledge(message.id)
"""

__all__ = [
    "BackpressureManager",
    "ConsumerErrorHandler",
    "MessageDeserializer",
    "StreamConsumer",
]
