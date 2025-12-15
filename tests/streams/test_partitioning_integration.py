"""Integration tests for stream partitioning with Redis.

Tests partition assignment, rebalancing, and message routing.
"""

import pytest
from redis.asyncio import Redis

from src.streams.redis_stream import RedisStream
from src.streams.partitioner import StreamPartitioner
from src.core.models import TelemetryEvent
from datetime import datetime, timezone


@pytest.mark.integration
@pytest.mark.asyncio
class TestStreamPartitioningIntegration:
    """Integration tests for stream partitioning."""

    async def test_partition_creation(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test creating multiple partitions."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        partitioner = StreamPartitioner(base_stream_name=test_stream_name, num_partitions=3)
        stream = RedisStream(url=redis_url)

        # Publish events to different partitions
        for i in range(9):
            event = TelemetryEvent(
                device_id=f"router-{i % 3}",
                interface="eth0",
                metric_name="cpu",
                metric_value=float(50 + i),
                timestamp=datetime.now(timezone.utc),
            )
            partition_name = partitioner.get_partition(event.device_id)
            await stream.publish(partition_name, event.model_dump())

        # Verify messages distributed across partitions
        partition_counts = {}
        for i in range(3):
            partition_name = partitioner.get_partition_name(i)
            messages = await redis_client.xread({partition_name: "0-0"}, count=10)
            if messages:
                count = len(messages[0][1])
                partition_counts[partition_name] = count

        # All partitions should have messages
        assert len(partition_counts) == 3
        total_messages = sum(partition_counts.values())
        assert total_messages == 9

        # Cleanup
        for i in range(3):
            partition_name = partitioner.get_partition_name(i)
            await redis_client.delete(partition_name)
        await redis_client.aclose()

    async def test_consistent_routing(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test same device_id always routes to same partition."""
        partitioner = StreamPartitioner(base_stream_name=test_stream_name, num_partitions=4)
        
        device_id = "router-special-01"
        partitions = set()

        # Send multiple events for same device
        for _ in range(10):
            partition_name = partitioner.get_partition(device_id)
            partitions.add(partition_name)

        # Should always route to same partition
        assert len(partitions) == 1

    async def test_partition_assignment(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test assigning partitions to workers."""
        partitioner = StreamPartitioner(base_stream_name=test_stream_name, num_partitions=6)

        # Assign partitions to 2 workers
        worker1_partitions = partitioner.assign_partitions(worker_id=0, total_workers=2)
        worker2_partitions = partitioner.assign_partitions(worker_id=1, total_workers=2)

        # Each worker should have 3 partitions
        assert len(worker1_partitions) == 3
        assert len(worker2_partitions) == 3

        # No overlap
        assert set(worker1_partitions).isdisjoint(set(worker2_partitions))

        # All partitions covered
        all_assigned = set(worker1_partitions) | set(worker2_partitions)
        all_partitions = {partitioner.get_partition_name(i) for i in range(6)}
        assert all_assigned == all_partitions

    async def test_rebalancing_on_worker_change(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test partition rebalancing when workers added/removed."""
        partitioner = StreamPartitioner(base_stream_name=test_stream_name, num_partitions=8)

        # Initially 2 workers
        initial_w1 = partitioner.assign_partitions(worker_id=0, total_workers=2)
        initial_w2 = partitioner.assign_partitions(worker_id=1, total_workers=2)

        assert len(initial_w1) == 4
        assert len(initial_w2) == 4

        # Add third worker
        new_w1 = partitioner.assign_partitions(worker_id=0, total_workers=3)
        new_w2 = partitioner.assign_partitions(worker_id=1, total_workers=3)
        new_w3 = partitioner.assign_partitions(worker_id=2, total_workers=3)

        # Distribution should be close to even (2-3 partitions each)
        assert len(new_w1) in (2, 3)
        assert len(new_w2) in (2, 3)
        assert len(new_w3) in (2, 3)

        # All partitions still covered
        all_assigned = set(new_w1) | set(new_w2) | set(new_w3)
        assert len(all_assigned) == 8

    async def test_publish_and_consume_from_partition(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test publishing and consuming from specific partition."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        partitioner = StreamPartitioner(base_stream_name=test_stream_name, num_partitions=2)
        stream = RedisStream(url=redis_url)

        device_id = "router-partition-test"
        partition_name = partitioner.get_partition(device_id)

        # Publish event
        event = TelemetryEvent(
            device_id=device_id,
            interface="eth0",
            metric_name="bandwidth",
            metric_value=100.0,
            timestamp=datetime.now(timezone.utc),
        )
        await stream.publish(partition_name, event.model_dump())

        # Create consumer group on partition
        consumer_group = f"{partition_name}-consumers"
        try:
            await stream.create_consumer_group(partition_name, consumer_group)
        except Exception:
            pass

        # Consume from partition
        messages = await stream.read_from_group(
            stream_name=partition_name,
            group_name=consumer_group,
            consumer_name="test-consumer",
            count=1,
        )

        assert len(messages) > 0
        message_data = messages[0]
        assert message_data.payload["device_id"] == device_id

        # Cleanup
        await redis_client.delete(partition_name)
        await redis_client.aclose()

    async def test_distribution_across_partitions(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test event distribution is balanced across partitions."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        partitioner = StreamPartitioner(base_stream_name=test_stream_name, num_partitions=4)
        stream = RedisStream(url=redis_url)

        # Publish events for many different devices
        for i in range(100):
            event = TelemetryEvent(
                device_id=f"device-{i}",
                interface="eth0",
                metric_name="test",
                metric_value=float(i),
                timestamp=datetime.now(timezone.utc),
            )
            partition_name = partitioner.get_partition(event.device_id)
            await stream.publish(partition_name, event.model_dump())

        # Count messages per partition
        partition_counts = []
        for i in range(4):
            partition_name = partitioner.get_partition_name(i)
            messages = await redis_client.xread({partition_name: "0-0"}, count=100)
            if messages:
                count = len(messages[0][1])
                partition_counts.append(count)
            else:
                partition_counts.append(0)

        # Total should be 100
        assert sum(partition_counts) == 100

        # Distribution should be reasonably balanced (each partition 15-35 messages)
        for count in partition_counts:
            assert 15 <= count <= 35, f"Unbalanced distribution: {partition_counts}"

        # Cleanup
        for i in range(4):
            partition_name = partitioner.get_partition_name(i)
            await redis_client.delete(partition_name)
        await redis_client.aclose()
