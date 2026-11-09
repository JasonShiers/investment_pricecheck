"""Tests for IO Utils."""
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from investment_prices.io_utils import write_prices
from investment_prices.models import GBPAmount, Holding, PriceResult


class TestIOUtils(TestCase):
    """Tests for IO Utils."""

    def test_write_prices_writes_bare_numbers(self) -> None:
        """Test write prices writes prices as numbers."""
        results = [
            PriceResult(
                Holding("ABC", "https://example.com/abc"),
                GBPAmount(Decimal("123.4")),
            ),
            PriceResult(Holding("DEF", "https://example.com/def"), None),
        ]

        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            output_path = tmp_path / "prices.csv"

            write_prices(output_path, results)

            content = output_path.read_text(encoding="utf-8")

        self.assertFalse("£" in content)
        lines = content.splitlines()
        self.assertEqual(lines[0], "Holding,GBP Price")
        self.assertEqual(lines[1], "ABC,123.4000")
        self.assertEqual(lines[2], "DEF,")
