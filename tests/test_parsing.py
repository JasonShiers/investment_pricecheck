"""Test amount parsing."""
from decimal import Decimal, InvalidOperation
from unittest import TestCase

from investment_prices.parsing import parse_amount


class TestParseAmount(TestCase):
    """Test amount parsing."""

    def test_parse_amount(self) -> None:
        """Test amounts in different formats."""
        test_cases = [
            ("1,234.50 GBP", Decimal("1234.50")),
            ("123.45p", Decimal("123.45")),
            ("£1,999", Decimal("1999")),
            ("  42.0  ", Decimal("42.0")),
        ]
        for text, expected in test_cases:
            with self.subTest(text=text, expected=expected):
                self.assertEqual(parse_amount(text), expected)

    def test_parse_amount_raises_when_no_number_present(self) -> None:
        """Error should be raised if string cannot be parsed."""
        with self.assertRaises(InvalidOperation):
            parse_amount("no price available")
