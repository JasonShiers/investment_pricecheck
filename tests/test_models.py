"""Tests for models."""
from dataclasses import FrozenInstanceError
from decimal import Decimal
from unittest import TestCase

from investment_prices.models import Currency, Price


class TestModels(TestCase):
    """Tests for models."""

    def test_price_str_formats_pence_with_lowercase_p(self) -> None:
        """GBX values should be formatted with p."""
        self.assertEqual(str(Price(Decimal("123.4"), Currency.GBX)), "123.40p")

    def test_price_str_formats_gbp_with_pound_sign(self) -> None:
        """GBP values should be formatted with £."""
        self.assertEqual(str(Price(Decimal("1.5"), Currency.GBP)), "£1.5000")

    def test_price_is_immutable(self) -> None:
        """Prices should be immutable."""
        price = Price(Decimal("1"), Currency.GBP)
        with self.assertRaises(FrozenInstanceError):
            price.amount = Decimal("2") # pyright: ignore[reportAttributeAccessIssue]
