"""Network device simulator.

Simulates network devices sending telemetry data to ingest service.
"""
import logging

_log = logging.getLogger(__name__)


async def run_simulator() -> None:
    """Run device simulator."""
    raise NotImplementedError


def main() -> None:
    """Main entry point."""
    raise NotImplementedError


if __name__ == "__main__":
    main()


__all__ = ["main", "run_simulator"]
