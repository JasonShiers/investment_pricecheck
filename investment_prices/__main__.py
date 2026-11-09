#!/usr/bin/env python
"""CLI entry point.

python -m investment_prices [--holdings ...] [--output ...]
"""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

from .app import run
from .browser import chrome_driver
from .config import Settings


def main() -> None:
    """Orchestrator function."""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s",
    )
    logger = logging.getLogger(__name__)
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    settings = Settings.from_args()
    with chrome_driver() as driver:
        results = run(driver, settings)
    for result in results:
        status = (
            f"£{result.price:.4f}" if result.price is not None else "FAILED"
        )
        logger.info("%s: %s", result.holding.symbol, status)


if __name__ == "__main__":
    main()
