"""Network device simulator.

Simulates network devices sending telemetry data to the Ingest service
for testing and demonstration purposes. Generates synthetic telemetry
data with configurable patterns and anomalies.

Architecture:
    - Simulates multiple network devices (routers, switches)
    - Generates telemetry for multiple interfaces per device
    - Sends HTTP POST requests to Ingest service
    - Can inject anomalies for testing detection

Communication:
    Output: HTTP POST to http://localhost:8000/telemetry

Metrics Simulated:
    - packet_loss_rate: Percentage of packets lost (0.0-1.0)
    - latency_ms: Network latency in milliseconds
    - bandwidth_utilization: Interface utilization (0.0-1.0)
    - error_rate: Error rate on interface (0.0-1.0)

Functions:
    run_simulator: Initialize and run the device simulator.
    main: Entry point for the simulator.

Example:
    Running the simulator::

        # Via Python module (recommended)
        python -m simulator

        # Direct module execution
        python -m simulator.main

        # Console script (after pip install -e .)
        telemetry-simulator

        # Via Docker Compose
        docker-compose up simulator

        # Sends telemetry every 1-5 seconds per device
"""

import asyncio
import logging as _log
import os
import random
import sys
from datetime import datetime, timezone

import httpx


async def send_telemetry(
    *,
    ingest_url: str,
    device_id: str,
    interface: str,
    metric_name: str,
    metric_value: float,
) -> bool:
    """Send telemetry data to ingest service.

    Args:
        ingest_url: Ingest service URL.
        device_id: Device identifier.
        interface: Interface name.
        metric_name: Metric name.
        metric_value: Metric value.

    Returns:
        True if successful, False otherwise.
    """
    payload = {
        "device_id": device_id,
        "interface": interface,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ingest_url}/api/v1/telemetry",
                json=payload,
                timeout=5.0,
            )
            response.raise_for_status()
            _log.debug(
                "Sent telemetry: device=%s, interface=%s, metric=%s, value=%f",
                device_id,
                interface,
                metric_name,
                metric_value,
            )
            return True
    except Exception as e:
        _log.error("Failed to send telemetry: %s", str(e))
        return False


def generate_metric_value(metric_name: str, is_anomaly: bool) -> float:
    """Generate metric value with optional anomaly.

    Args:
        metric_name: Metric name.
        is_anomaly: Whether to generate anomalous value.

    Returns:
        Metric value.
    """
    ranges = {
        "packet_loss_rate": {
            "normal": (0.01, 0.05),
            "anomaly": (0.15, 0.30),
        },
        "latency_ms": {
            "normal": (5.0, 20.0),
            "anomaly": (100.0, 500.0),
        },
        "bandwidth_utilization": {
            "normal": (0.3, 0.7),
            "anomaly": (0.85, 0.99),
        },
        "error_rate": {
            "normal": (0.001, 0.01),
            "anomaly": (0.05, 0.15),
        },
        "cpu_utilization": {
            "normal": (40.0, 75.0),
            "anomaly": (85.0, 99.0),
        },
    }

    if metric_name not in ranges:
        return random.uniform(0.0, 100.0)

    range_type = "anomaly" if is_anomaly else "normal"
    min_val, max_val = ranges[metric_name][range_type]
    generated_value = random.uniform(min_val, max_val)
    return generated_value


async def simulate_device(
    *,
    device_id: str,
    interfaces: list[str],
    metrics: list[str],
    ingest_url: str,
    interval_seconds: float,
    anomaly_rate: float,
) -> None:
    """Simulate a single device sending telemetry.

    Args:
        device_id: Device identifier.
        interfaces: List of interface names.
        metrics: List of metric names.
        ingest_url: Ingest service URL.
        interval_seconds: Seconds between telemetry.
        anomaly_rate: Probability of anomaly (0.0-1.0).
    """
    _log.info("Starting simulator for device: %s", device_id)

    while True:
        try:
            for interface in interfaces:
                for metric_name in metrics:
                    is_anomaly = random.random() < anomaly_rate

                    metric_value = generate_metric_value(metric_name, is_anomaly)

                    await send_telemetry(
                        ingest_url=ingest_url,
                        device_id=device_id,
                        interface=interface,
                        metric_name=metric_name,
                        metric_value=metric_value,
                    )

            await asyncio.sleep(interval_seconds)

        except asyncio.CancelledError:
            _log.info("Simulator stopped for device: %s", device_id)
            break
        except Exception as e:
            _log.error("Error in simulator for %s: %s", device_id, str(e))
            await asyncio.sleep(interval_seconds)


async def run_simulator() -> None:
    """Run device simulator.

    Simulates multiple network devices sending telemetry data to the
    Ingest service. Each device has multiple interfaces that report
    metrics at regular intervals.

    Simulation Strategy:
        - 5-10 simulated devices (routers/switches)
        - 2-4 interfaces per device (eth0, eth1, etc.)
        - 4-6 metrics per interface
        - Telemetry sent every 1-5 seconds
        - Occasional anomalies injected (10% chance)

    Devices Simulated:
        - router-01, router-02, router-03
        - switch-01, switch-02

    Interfaces:
        - eth0, eth1, eth2, eth3

    Metrics:
        - packet_loss_rate (normal: 0.01-0.05, anomaly: 0.15-0.30)
        - latency_ms (normal: 5-20ms, anomaly: 100-500ms)
        - bandwidth_utilization (normal: 0.3-0.7, anomaly: 0.85-0.99)
        - error_rate (normal: 0.001-0.01, anomaly: 0.05-0.15)

    Raises:
        ConnectionError: If cannot connect to Ingest service.

    Example:
        await run_simulator()  # Runs until interrupted
    """
    num_devices = int(os.getenv("SIMULATOR_NUM_DEVICES", "5"))
    interval_seconds = float(os.getenv("SIMULATOR_INTERVAL_SECONDS", "2"))
    anomaly_rate = float(os.getenv("SIMULATOR_ANOMALY_RATE", "0.1"))
    ingest_url = os.getenv("INGEST_URL", "http://localhost:8000")

    devices = [f"router-{i:02d}" for i in range(1, num_devices + 1)]
    interfaces = ["eth0", "eth1", "eth2"]
    metrics = [
        "packet_loss_rate",
        "latency_ms",
        "bandwidth_utilization",
        "error_rate",
        "cpu_utilization",
    ]

    _log.info(
        "Starting simulator: devices=%d, interval=%fs, anomaly_rate=%f",
        num_devices,
        interval_seconds,
        anomaly_rate,
    )

    tasks = [
        asyncio.create_task(
            simulate_device(
                device_id=device_id,
                interfaces=interfaces,
                metrics=metrics,
                ingest_url=ingest_url,
                interval_seconds=interval_seconds,
                anomaly_rate=anomaly_rate,
            )
        )
        for device_id in devices
    ]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        _log.info("Simulator shutting down...")
        for task in tasks:
            task.cancel()


def main() -> int:
    """Main entry point for the simulator.

    Loads configuration and runs the async simulator using asyncio.

    Configuration:
        - SIMULATOR_NUM_DEVICES: Number of devices to simulate (default: 5)
        - SIMULATOR_INTERVAL_SECONDS: Telemetry interval (default: 2)
        - SIMULATOR_ANOMALY_RATE: Probability of anomaly (default: 0.1)
        - INGEST_URL: Ingest service URL (default: http://localhost:8000)

    Returns:
        Exit code:
            - 0: Success - simulator stopped cleanly
            - 1: Configuration error - invalid configuration provided
            - 2: Connection error - failed to connect to ingest service
            - 3: Runtime error - unexpected error during simulation

    Example:
        Running with custom configuration::

            # With defaults (recommended)
            python -m simulator

            # Or with console script
            telemetry-simulator

            # With more devices
            SIMULATOR_NUM_DEVICES=10 python -m simulator

            # Custom ingest URL
            INGEST_URL=http://ingest:8000 python -m simulator
    """
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging_numeric_level = getattr(_log, log_level.upper(), _log.INFO)

    _log.basicConfig(
        level=logging_numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        asyncio.run(run_simulator())
        return 0
    except KeyboardInterrupt:
        _log.info("Simulator stopped by user")
        return 0
    except ValueError as e:
        _log.error("Configuration error: %s", str(e))
        return 1
    except ConnectionError as e:
        _log.error("Connection error: %s", str(e))
        return 2
    except Exception as e:
        _log.error("Runtime error: %s", str(e))
        return 3


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["main", "run_simulator", "send_telemetry", "generate_metric_value", "simulate_device"]
