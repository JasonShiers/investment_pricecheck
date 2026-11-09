"""Runtime configuration for the price checker.

Settings is a plain, immutable value object built
from CLI args (with the old paths kept only as defaults), so the rest
of the code just takes a Settings instance as a parameter.
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

HOLDINGS_ENV_VAR = "HOLDINGS_PATH"
PRICES_ENV_VAR = "PRICES_PATH"


def _path(value: str) -> Path:
    """Parse a path argument, expanding a leading ``~``."""
    return Path(value).expanduser()


@dataclass(frozen=True, slots=True)
class Settings:
    """Settings for input/output and lookup retries."""

    holdings_path: Path
    prices_path: Path
    max_retries: int = 10

    @classmethod
    def from_args(
        cls,
        argv: list[str] | None = None,
        env: Mapping[str, str] | None = None,
    ) -> Settings:
        """Construct Settings object.

        from CLI arguments, falling back to env  vars.
        """
        env = os.environ if env is None else env
        holdings_default = env.get(HOLDINGS_ENV_VAR) or None
        prices_default = env.get(PRICES_ENV_VAR) or None

        parser = argparse.ArgumentParser(
            description="Fetch investment holding prices.",
        )
        parser.add_argument(
            "--holdings",
            type=_path,
            default=holdings_default,
            required=holdings_default is None,
            help="CSV of symbol,url to look up prices for",
        )
        parser.add_argument(
            "--output",
            type=_path,
            default=prices_default,
            required=prices_default is None,
            help="Where to write the resulting prices CSV",
        )
        parser.add_argument(
            "--max-retries",
            type=int,
            default=3,
            help="Maximum attempts per holding before giving up",
        )
        args = parser.parse_args(argv)
        return cls(
            holdings_path=args.holdings,
            prices_path=args.output,
            max_retries=args.max_retries,
        )
