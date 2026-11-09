"""Core value objects for investment price lookup.

These are plain, immutable data holders with no I/O and no external
dependencies, which makes them trivial to construct and compare in
tests.
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import NewType


class Currency(StrEnum):
    """Currencies that can appear on a broker's page."""

    GBP = "GBP"
    GBX = "GBX"
    USD = "USD"


@dataclass(frozen=True, slots=True)
class Price:
    """An immutable amount of money in a given currency."""

    amount: Decimal
    currency: Currency

    def __str__(self) -> str:
        """Get string representation."""
        if self.currency is Currency.GBX:
            return f"{self.amount:.2f}p"
        symbol = {
            Currency.GBP: "\u00a3", Currency.USD: "$",
        }.get(self.currency, "")
        return f"{symbol}{self.amount:.4f}"


# A Decimal that has already been through CurrencyConverter.to_gbp
GBPAmount = NewType("GBPAmount", Decimal)


@dataclass(frozen=True, slots=True)
class Holding:
    """A single line from holdings.csv: what to look up, and where."""

    symbol: str
    url: str


@dataclass(frozen=True, slots=True)
class PriceResult:
    """The outcome of looking up one holding. price is None on failure."""

    holding: Holding
    price: GBPAmount | None
