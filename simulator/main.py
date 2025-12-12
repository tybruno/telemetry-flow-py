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

        # Via Python module
        python -m simulator.main
        
        # Via Docker Compose
        docker-compose up simulator
        
        # Sends telemetry every 1-5 seconds per device
"""

import logging

_log = logging.getLogger(__name__)


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
    raise NotImplementedError


def main() -> None:
    """Main entry point for the simulator.
    
    Loads configuration and runs the async simulator using asyncio.
    
    Configuration:
        - SIMULATOR_NUM_DEVICES: Number of devices to simulate (default: 5)
        - SIMULATOR_INTERVAL_SECONDS: Telemetry interval (default: 2)
        - SIMULATOR_ANOMALY_RATE: Probability of anomaly (default: 0.1)
        - INGEST_URL: Ingest service URL (default: http://localhost:8000)
    
    Example:
        Running with custom configuration::
        
            # With defaults
            python -m simulator.main
            
            # With more devices
            SIMULATOR_NUM_DEVICES=10 python -m simulator.main
            
            # Custom ingest URL
            INGEST_URL=http://ingest:8000 python -m simulator.main
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()


__all__ = ["main", "run_simulator"]
