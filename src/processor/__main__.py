"""Allow running processor worker as a module.

This enables running the processor worker using:
    python -m src.processor
"""

from src.processor.main import main

if __name__ == "__main__":
    main()
