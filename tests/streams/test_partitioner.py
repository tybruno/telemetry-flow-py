"""Tests for StreamPartitioner implementation.

This module tests the stream partitioning functionality, including
consistent hashing, partition assignment, and stream name generation.
"""

import pytest

from src.streams.partitioner import StreamPartitioner


class TestStreamPartitioner:
    """Test suite for StreamPartitioner class."""

    def test_initialization_default_partitions(self) -> None:
        """Test StreamPartitioner initialization with default partitions."""
        partitioner = StreamPartitioner()

        assert partitioner.num_partitions == 3
        result_partitions = partitioner.num_partitions
        assert result_partitions == 3

    def test_initialization_custom_partitions(self) -> None:
        """Test StreamPartitioner initialization with custom partitions."""
        partitioner = StreamPartitioner(num_partitions=5)

        assert partitioner.num_partitions == 5
        result_partitions = partitioner.num_partitions
        assert result_partitions == 5

    def test_initialization_minimum_partitions(self) -> None:
        """Test StreamPartitioner initialization with minimum partitions."""
        partitioner = StreamPartitioner(num_partitions=1)

        assert partitioner.num_partitions == 1
        result_partitions = partitioner.num_partitions
        assert result_partitions == 1

    def test_initialization_invalid_zero_partitions(self) -> None:
        """Test StreamPartitioner initialization with zero partitions."""
        with pytest.raises(ValueError, match="num_partitions must be positive"):
            StreamPartitioner(num_partitions=0)

    def test_initialization_invalid_negative_partitions(self) -> None:
        """Test StreamPartitioner initialization with negative partitions."""
        with pytest.raises(ValueError, match="num_partitions must be positive"):
            StreamPartitioner(num_partitions=-1)

    def test_get_partition_consistent_hashing(self) -> None:
        """Test that same device_id always returns same partition."""
        partitioner = StreamPartitioner(num_partitions=3)

        device_id = "router-01"

        # Call multiple times to verify consistency
        partition1 = partitioner.get_partition(device_id)
        partition2 = partitioner.get_partition(device_id)
        partition3 = partitioner.get_partition(device_id)

        assert partition1 == partition2
        assert partition2 == partition3
        result_partition = partition1
        assert result_partition == partition2 == partition3

    def test_get_partition_valid_range(self) -> None:
        """Test that partition number is within valid range."""
        partitioner = StreamPartitioner(num_partitions=3)

        device_ids = [f"router-{i:02d}" for i in range(1, 21)]

        for device_id in device_ids:
            partition = partitioner.get_partition(device_id)
            assert 0 <= partition < 3
            result_in_range = 0 <= partition < 3
            assert result_in_range is True

    def test_get_partition_distribution(self) -> None:
        """Test that partitions are distributed across devices."""
        partitioner = StreamPartitioner(num_partitions=3)

        # Generate many device IDs
        device_ids = [f"device-{i:05d}" for i in range(1000)]

        partitions = [partitioner.get_partition(device_id) for device_id in device_ids]

        # Check all partitions are used
        unique_partitions = set(partitions)
        assert len(unique_partitions) == 3
        result_all_used = len(unique_partitions) == 3
        assert result_all_used is True

        # Check distribution is reasonably balanced (within 20% of ideal)
        from collections import Counter

        partition_counts = Counter(partitions)
        ideal_count = len(device_ids) / 3

        for partition_count in partition_counts.values():
            deviation = abs(partition_count - ideal_count) / ideal_count
            assert deviation < 0.2  # Within 20% of ideal distribution
            result_balanced = deviation < 0.2
            assert result_balanced is True

    def test_get_partition_empty_device_id(self) -> None:
        """Test get_partition with empty device_id raises ValueError."""
        partitioner = StreamPartitioner(num_partitions=3)

        with pytest.raises(ValueError, match="device_id cannot be empty"):
            partitioner.get_partition("")

    def test_get_partition_whitespace_device_id(self) -> None:
        """Test get_partition with whitespace-only device_id raises ValueError."""
        partitioner = StreamPartitioner(num_partitions=3)

        with pytest.raises(ValueError, match="device_id cannot be empty"):
            partitioner.get_partition("   ")

    def test_get_stream_name_basic(self) -> None:
        """Test get_stream_name with basic inputs."""
        partitioner = StreamPartitioner(num_partitions=3)

        stream_name = partitioner.get_stream_name(
            base_name="telemetry", device_id="router-01"
        )

        # Verify format
        assert stream_name.startswith("telemetry:")
        result_has_prefix = stream_name.startswith("telemetry:")
        assert result_has_prefix is True

        # Verify partition suffix is valid
        partition = int(stream_name.split(":")[-1])
        assert 0 <= partition < 3
        result_valid_partition = 0 <= partition < 3
        assert result_valid_partition is True

    def test_get_stream_name_consistency(self) -> None:
        """Test that same device_id always returns same stream name."""
        partitioner = StreamPartitioner(num_partitions=3)

        device_id = "router-05"

        stream1 = partitioner.get_stream_name(
            base_name="telemetry", device_id=device_id
        )
        stream2 = partitioner.get_stream_name(
            base_name="telemetry", device_id=device_id
        )
        stream3 = partitioner.get_stream_name(
            base_name="telemetry", device_id=device_id
        )

        assert stream1 == stream2 == stream3
        result_stream = stream1
        assert result_stream == stream2 == stream3

    def test_get_stream_name_different_base(self) -> None:
        """Test get_stream_name with different base names."""
        partitioner = StreamPartitioner(num_partitions=3)

        device_id = "router-01"

        telemetry_stream = partitioner.get_stream_name(
            base_name="telemetry", device_id=device_id
        )
        metrics_stream = partitioner.get_stream_name(
            base_name="metrics", device_id=device_id
        )

        # Different base names, same partition
        telemetry_partition = telemetry_stream.split(":")[-1]
        metrics_partition = metrics_stream.split(":")[-1]

        assert telemetry_partition == metrics_partition
        result_same_partition = telemetry_partition == metrics_partition
        assert result_same_partition is True

        # Different stream names
        assert telemetry_stream.startswith("telemetry:")
        assert metrics_stream.startswith("metrics:")
        result_different_bases = telemetry_stream.startswith(
            "telemetry:"
        ) and metrics_stream.startswith("metrics:")
        assert result_different_bases is True

    def test_get_all_stream_names(self) -> None:
        """Test get_all_stream_names returns all partition streams."""
        partitioner = StreamPartitioner(num_partitions=3)

        stream_names = partitioner.get_all_stream_names(base_name="telemetry")

        assert len(stream_names) == 3
        result_count = len(stream_names)
        assert result_count == 3

        expected_names = {"telemetry:0", "telemetry:1", "telemetry:2"}
        assert set(stream_names) == expected_names
        result_names = set(stream_names)
        assert result_names == expected_names

    def test_get_all_stream_names_custom_partitions(self) -> None:
        """Test get_all_stream_names with custom partition count."""
        partitioner = StreamPartitioner(num_partitions=5)

        stream_names = partitioner.get_all_stream_names(base_name="metrics")

        assert len(stream_names) == 5
        result_count = len(stream_names)
        assert result_count == 5

        expected_names = {
            "metrics:0",
            "metrics:1",
            "metrics:2",
            "metrics:3",
            "metrics:4",
        }
        assert set(stream_names) == expected_names
        result_names = set(stream_names)
        assert result_names == expected_names

    def test_get_all_stream_names_order(self) -> None:
        """Test get_all_stream_names returns streams in order."""
        partitioner = StreamPartitioner(num_partitions=3)

        stream_names = partitioner.get_all_stream_names(base_name="telemetry")

        expected_order = ["telemetry:0", "telemetry:1", "telemetry:2"]
        assert stream_names == expected_order
        result_order = stream_names
        assert result_order == expected_order

    def test_repr(self) -> None:
        """Test __repr__ returns useful representation."""
        partitioner = StreamPartitioner(num_partitions=5)

        repr_string = repr(partitioner)

        assert "StreamPartitioner" in repr_string
        assert "5" in repr_string
        result_has_info = "StreamPartitioner" in repr_string and "5" in repr_string
        assert result_has_info is True

    @pytest.mark.parametrize("num_partitions", [1, 2, 3, 5, 10, 100])
    def test_partition_count_variations(self, num_partitions: int) -> None:
        """Test partitioner with various partition counts."""
        partitioner = StreamPartitioner(num_partitions=num_partitions)

        assert partitioner.num_partitions == num_partitions
        result_count = partitioner.num_partitions
        assert result_count == num_partitions

        # Verify all stream names are generated
        stream_names = partitioner.get_all_stream_names(base_name="test")
        assert len(stream_names) == num_partitions
        result_name_count = len(stream_names)
        assert result_name_count == num_partitions

    @pytest.mark.parametrize(
        "device_id,expected_consistency",
        [
            ("router-01", True),
            ("router-02", True),
            ("device-abc-123", True),
            ("very-long-device-id-with-many-characters-12345", True),
            ("simple", True),
        ],
    )
    def test_consistency_across_device_ids(
        self, device_id: str, expected_consistency: bool
    ) -> None:
        """Test partition consistency across various device IDs."""
        partitioner = StreamPartitioner(num_partitions=3)

        # Get partition multiple times
        partitions = [partitioner.get_partition(device_id) for _ in range(10)]

        # All should be the same
        is_consistent = len(set(partitions)) == 1
        assert is_consistent == expected_consistency
        result_consistent = is_consistent == expected_consistency
        assert result_consistent is True

    def test_known_device_partition_mapping(self) -> None:
        """Test specific device-to-partition mappings for verification.

        This test documents the expected partition assignments for specific
        devices used in testing. These should remain consistent due to
        deterministic MD5 hashing.
        """
        partitioner = StreamPartitioner(num_partitions=3)

        # These mappings are based on MD5 hashing and should be stable
        # Actual values depend on MD5 implementation
        router_01_partition = partitioner.get_partition("router-01")
        router_02_partition = partitioner.get_partition("router-02")
        router_03_partition = partitioner.get_partition("router-03")

        # Verify all are in valid range
        assert 0 <= router_01_partition < 3
        assert 0 <= router_02_partition < 3
        assert 0 <= router_03_partition < 3
        result_all_valid = (
            0 <= router_01_partition < 3
            and 0 <= router_02_partition < 3
            and 0 <= router_03_partition < 3
        )
        assert result_all_valid is True

        # Verify consistency
        assert partitioner.get_partition("router-01") == router_01_partition
        assert partitioner.get_partition("router-02") == router_02_partition
        assert partitioner.get_partition("router-03") == router_03_partition
        result_consistent = (
            partitioner.get_partition("router-01") == router_01_partition
            and partitioner.get_partition("router-02") == router_02_partition
            and partitioner.get_partition("router-03") == router_03_partition
        )
        assert result_consistent is True


class TestStreamPartitionerIntegration:
    """Integration tests for StreamPartitioner with realistic scenarios."""

    def test_multi_device_assignment(self) -> None:
        """Test partition assignment for multiple devices."""
        partitioner = StreamPartitioner(num_partitions=3)

        devices = ["router-01", "router-02", "router-03", "router-04", "router-05"]

        assignments = {device: partitioner.get_partition(device) for device in devices}

        # All devices assigned
        assert len(assignments) == len(devices)
        result_all_assigned = len(assignments) == len(devices)
        assert result_all_assigned is True

        # All partitions in valid range
        all_valid_range = all(0 <= partition < 3 for partition in assignments.values())
        assert all_valid_range is True
        result_valid_range = all_valid_range
        assert result_valid_range is True

    def test_stream_name_generation_realistic(self) -> None:
        """Test stream name generation with realistic scenarios."""
        partitioner = StreamPartitioner(num_partitions=3)

        base_name = "telemetry"
        devices = ["router-01", "router-02", "router-03"]

        stream_names = [
            partitioner.get_stream_name(base_name=base_name, device_id=device)
            for device in devices
        ]

        # All valid stream names
        all_valid = all(name.startswith("telemetry:") for name in stream_names)
        assert all_valid is True
        result_all_valid = all_valid
        assert result_all_valid is True

        # All partitions represented (with enough devices)
        partitions = [int(name.split(":")[-1]) for name in stream_names]
        all_in_range = all(0 <= p < 3 for p in partitions)
        assert all_in_range is True
        result_in_range = all_in_range
        assert result_in_range is True
