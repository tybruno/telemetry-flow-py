"""Processor worker entry point.

Main entry point for running telemetry processor workers.
"""
import logging

_log = logging.getLogger(__name__)


async def run_worker() -> None:
    """Run the telemetry processor worker."""
    raise NotImplementedError


def main() -> None:
    """Main entry point."""
    raise NotImplementedError


if __name__ == "__main__":
    main()


__all__ = ["main", "run_worker"]
