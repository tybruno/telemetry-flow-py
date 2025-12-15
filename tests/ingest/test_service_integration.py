"""Integration tests for ingest service with Redis Streams.

Tests FastAPI endpoints and Redis Stream publishing.
"""

import pytest
from datetime import datetime, timezone
from httpx import AsyncClient
from redis.asyncio import Redis

from src.ingest.service import IngestService, create_app
from src.streams.redis_stream import RedisStream
from src.core.models import TelemetryEvent


@pytest.mark.integration
@pytest.mark.asyncio
class TestIngestServiceIntegration:
    """Integration tests for ingest service with real Redis."""

    async def test_health_check_endpoint(self, redis_url: str) -> None:
        """Test health check endpoint returns healthy status."""
        stream = RedisStream(url=redis_url)
        app = create_app(stream=stream, stream_name="test-stream")

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "version" in data

    async def test_ingest_telemetry_endpoint(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test ingesting telemetry via HTTP endpoint."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        stream = RedisStream(url=redis_url)
        app = create_app(stream=stream, stream_name=test_stream_name)

        telemetry_data = {
            "device_id": "router-01",
            "interface": "eth0",
            "metric_name": "cpu_utilization",
            "metric_value": 75.5,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/telemetry", json=telemetry_data)
            assert response.status_code == 200
            data = response.json()
            assert "message_id" in data
            assert data["status"] == "ingested"

        # Verify message in stream
        messages = await redis_client.xread({test_stream_name: "0-0"}, count=1)
        assert len(messages) > 0
        stream_data = messages[0][1][0]
        assert b"device_id" in stream_data[1]

        # Cleanup
        await redis_client.delete(test_stream_name)
        await redis_client.aclose()

    async def test_invalid_telemetry_data(self, redis_url: str) -> None:
        """Test validation of invalid telemetry data."""
        stream = RedisStream(url=redis_url)
        app = create_app(stream=stream, stream_name="test-stream")

        invalid_data = {
            "device_id": "",  # Empty device_id
            "interface": "eth0",
            "metric_name": "cpu",
            "metric_value": -10.0,  # Invalid negative value
        }

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/telemetry", json=invalid_data)
            assert response.status_code == 422  # Validation error

    async def test_concurrent_ingest_requests(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test handling multiple concurrent ingest requests."""
        import asyncio

        redis_client = Redis.from_url(redis_url, decode_responses=False)
        stream = RedisStream(url=redis_url)
        app = create_app(stream=stream, stream_name=test_stream_name)

        async def send_telemetry(device_num: int):
            telemetry_data = {
                "device_id": f"router-{device_num:02d}",
                "interface": "eth0",
                "metric_name": "bandwidth",
                "metric_value": float(50 + device_num),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post("/telemetry", json=telemetry_data)
                return response.status_code

        # Send 10 concurrent requests
        tasks = [send_telemetry(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert all(status == 200 for status in responses)

        # Verify all messages in stream
        messages = await redis_client.xread({test_stream_name: "0-0"}, count=10)
        assert len(messages) > 0
        assert len(messages[0][1]) == 10

        # Cleanup
        await redis_client.delete(test_stream_name)
        await redis_client.aclose()

    async def test_service_direct_ingest(
        self, redis_url: str, test_stream_name: str
    ) -> None:
        """Test direct ingest service method (not via HTTP)."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        stream = RedisStream(url=redis_url)
        service = IngestService(stream=stream, stream_name=test_stream_name)

        event = TelemetryEvent(
            device_id="switch-01",
            interface="port-1",
            metric_name="packet_loss",
            metric_value=0.5,
            timestamp=datetime.now(timezone.utc),
        )

        message_id = await service.ingest_telemetry(event)
        assert message_id is not None
        assert "-" in message_id  # Redis message ID format

        # Verify in stream
        messages = await redis_client.xread({test_stream_name: "0-0"}, count=1)
        assert len(messages) > 0

        # Cleanup
        await redis_client.delete(test_stream_name)
        await redis_client.aclose()

    async def test_metrics_endpoint(self, redis_url: str) -> None:
        """Test metrics endpoint returns processing statistics."""
        stream = RedisStream(url=redis_url)
        app = create_app(stream=stream, stream_name="test-stream")

        async with AsyncClient(app=app, base_url="http://test") as client:
            # Ingest some telemetry first
            for i in range(5):
                telemetry_data = {
                    "device_id": f"device-{i}",
                    "interface": "eth0",
                    "metric_name": "test_metric",
                    "metric_value": float(i),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await client.post("/telemetry", json=telemetry_data)

            # Check metrics
            response = await client.get("/metrics")
            assert response.status_code == 200
            data = response.json()
            assert "total_ingested" in data
            assert data["total_ingested"] >= 5
