"""Tests for currency conversions."""
from decimal import Decimal
from unittest import TestCase

from investment_prices.currency import CurrencyConverter
from investment_prices.models import Currency, Price


class TestCurrencyConverter(TestCase):
    """Tests for CurrencyConverter."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create dummy converter."""
        cls.converter = CurrencyConverter(usd_gbp_rate=Decimal("0.8"))
        return super().setUpClass()

    def test_gbp_passes_through_unchanged(self) -> None:
        """GBP price should not change."""
        price = Price(Decimal("10"), Currency.GBP)
        self.assertEqual(self.converter.to_gbp(price), Decimal(10))


    def test_gbx_is_divided_by_100(self) -> None:
        """GBX to GBP should divide by 100."""
        price = Price(Decimal("250"), Currency.GBX)
        self.assertEqual(self.converter.to_gbp(price), Decimal("2.5"))


    def test_usd_is_multiplied_by_the_rate(self) -> None:
        """USD to GBP should multiply by the exchange rate."""
        price = Price(Decimal("100"), Currency.USD)
        self.assertEqual(self.converter.to_gbp(price), Decimal("80.0"))
