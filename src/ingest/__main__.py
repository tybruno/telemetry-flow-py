"""Allow running ingest service as a module.

This enables running the ingest service using:
    python -m src.ingest
"""

from src.ingest.main import main

if __name__ == "__main__":
    main()
