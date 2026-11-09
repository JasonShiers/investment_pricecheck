"""Tests for extractors."""
from decimal import Decimal
from unittest import TestCase
from urllib.parse import urlparse

from investment_prices.extractors import (
    AJBellExtractor,
    HLExtractor,
    IWebExtractor,
    LSEExtractor,
    get_extractor,
)
from investment_prices.models import Currency, Price


class TestExtractors(TestCase):
    """Tests for extractors."""

    def test_iweb_parse(self) -> None:
        """IWeb extractor should recognise GBX price."""
        self.assertEqual(
            IWebExtractor.parse("1,234.50 GBX"),
            Price(Decimal("1234.50"), Currency.GBX),
        )

    def test_hl_parse_is_always_pence(self) -> None:
        """HL extractor should recognise GBX price."""
        self.assertEqual(
            HLExtractor.parse("1,234.50p"),
            Price(Decimal("1234.50"), Currency.GBX),
        )

    def test_ajbell_parse_detects_pounds(self) -> None:
        """AJBell extractor should recognise GBP price."""
        self.assertEqual(
            AJBellExtractor.parse("£1,234.50"),
            Price(Decimal("1234.50"), Currency.GBP),
        )

    def test_ajbell_parse_detects_pence(self) -> None:
        """AJBell extractor should recognise GBX price."""
        self.assertEqual(
            AJBellExtractor.parse("123.4p"),
            Price(Decimal("123.4"), Currency.GBX),
        )

    def test_ajbell_parse_rejects_unrecognised_format(self) -> None:
        """AJBell extractor should reject invalid value."""
        self.assertIsNone(AJBellExtractor.parse("n/a"))

    def test_lse_parse_combines_price_and_currency_elements(self) -> None:
        """LSE extractor should combine price and currency correctly."""
        result = LSEExtractor.parse("1,234.50", "Price (GBX)")
        self.assertEqual(result, Price(Decimal("1234.50"), Currency.GBX))

    def test_get_extractor_matches_on_hostname(self) -> None:
        """Get extractor should recognise URL."""
        url = "https://www.hl.co.uk/shares/some-fund"
        self.assertIsInstance(get_extractor(url), HLExtractor)
        self.assertEqual(urlparse(url).netloc, "www.hl.co.uk")
