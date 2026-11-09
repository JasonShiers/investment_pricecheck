"""Currency conversion to GBP."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from .models import Currency, GBPAmount, Price


class ExchangeRateProvider(Protocol):
    """Anything that can supply the current USD -> GBP rate."""

    def usd_to_gbp_rate(self) -> Decimal: ...  # noqa: D102


@dataclass(frozen=True, slots=True)
class CurrencyConverter:
    """Converts a Price in any supported currency into GBP."""

    usd_gbp_rate: Decimal

    def to_gbp(self, price: Price) -> GBPAmount:
        """Normalise price to GBP."""
        match price.currency:
            case Currency.GBP:
                return GBPAmount(price.amount)
            case Currency.GBX:
                return GBPAmount(price.amount / 100)
            case Currency.USD:
                return GBPAmount(price.amount * self.usd_gbp_rate)
        msg = f"Currency {price.currency} not supported"
        raise NotImplementedError(msg)
