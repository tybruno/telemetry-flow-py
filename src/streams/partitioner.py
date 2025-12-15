"""Stream partitioning for horizontal scaling.

Provides deterministic partitioning of telemetry events to enable
horizontal scaling while maintaining per-device data locality.

Classes:
    StreamPartitioner: Assigns events to partitions based on device_id.

Example:
    partitioner = StreamPartitioner(num_partitions=3)
    partition = partitioner.get_partition("router-01")
    stream_name = partitioner.get_stream_name("telemetry", "router-01")
"""

import hashlib
import logging as _log


class StreamPartitioner:
    """Partitions events to streams for horizontal scaling.

    Uses consistent hashing on device_id to assign events to partitions.
    Ensures all events from same device go to same partition, enabling
    stateful aggregation with local in-memory windows.

    Attributes:
        _num_partitions: Total number of partitions.
        _base_stream_name: Base name for streams (e.g., "telemetry").

    Example:
        # Create partitioner for 3 partitions
        partitioner = StreamPartitioner(num_partitions=3)
        
        # Get partition for device
        partition = partitioner.get_partition("router-01")
        
        # Get full stream name
        stream = partitioner.get_stream_name("telemetry", "router-01")
        # Returns: "telemetry:0", "telemetry:1", or "telemetry:2"
    """

    __slots__ = ("_num_partitions", "_base_stream_name")

    _num_partitions: int
    _base_stream_name: str

    def __init__(self, *, num_partitions: int, base_stream_name: str = "telemetry") -> None:
        """Initialize stream partitioner.

        Args:
            num_partitions: Total number of partitions (must be > 0).
            base_stream_name: Base name for partitioned streams.

        Raises:
            ValueError: If num_partitions <= 0.

        Example:
            partitioner = StreamPartitioner(num_partitions=3)
        """
        if num_partitions <= 0:
            error_message = "num_partitions must be positive: %d"
            _log.error(error_message, num_partitions)
            raise ValueError(f"Invalid num_partitions: {num_partitions}") from None

        self._num_partitions = num_partitions
        self._base_stream_name = base_stream_name

        _log.info(
            "StreamPartitioner initialized: partitions=%d, base=%s",
            num_partitions,
            base_stream_name,
        )

    def get_partition(self, device_id: str) -> int:
        """Get partition number for device_id.

        Uses consistent hashing (MD5) to deterministically assign
        devices to partitions. Same device_id always maps to same
        partition.

        Args:
            device_id: Device identifier to partition.

        Returns:
            Partition number (0 to num_partitions-1).

        Raises:
            ValueError: If device_id is empty.

        Example:
            partition = partitioner.get_partition("router-01")
            # Returns: 0, 1, or 2 (for 3 partitions)
        """
        if not device_id or not device_id.strip():
            error_message = "device_id cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        # Use MD5 hash for deterministic partitioning
        hash_bytes = hashlib.md5(device_id.encode("utf-8")).digest()
        hash_value = int.from_bytes(hash_bytes[:4], byteorder="big")
        
        partition_number = hash_value % self._num_partitions
        return partition_number

    def get_stream_name(self, base_name: str, device_id: str) -> str:
        """Get partitioned stream name for device_id.

        Args:
            base_name: Base stream name (e.g., "telemetry").
            device_id: Device identifier.

        Returns:
            Partitioned stream name (e.g., "telemetry:0").

        Example:
            stream = partitioner.get_stream_name("telemetry", "router-01")
            # Returns: "telemetry:2" (or 0, 1 depending on hash)
        """
        partition = self.get_partition(device_id)
        stream_name = f"{base_name}:{partition}"
        return stream_name

    @property
    def num_partitions(self) -> int:
        """Get number of partitions.

        Returns:
            Total number of partitions.
        """
        return self._num_partitions

    def get_all_stream_names(self, base_name: str) -> list[str]:
        """Get all partition stream names.

        Args:
            base_name: Base stream name.

        Returns:
            List of all partitioned stream names.

        Example:
            streams = partitioner.get_all_stream_names("telemetry")
            # Returns: ["telemetry:0", "telemetry:1", "telemetry:2"]
        """
        stream_names = [
            f"{base_name}:{partition}"
            for partition in range(self._num_partitions)
        ]
        return stream_names


__all__ = ["StreamPartitioner"]
