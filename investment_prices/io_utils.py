"""Reading holdings and writing price results as CSV."""
import csv
from pathlib import Path

from .models import Holding, PriceResult

_HOLDINGS_HEADER = ["symbol", "url"]


def read_holdings(path: Path) -> list[Holding]:
    """Read the symbol/url pairs to look up prices for."""
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != _HOLDINGS_HEADER:
            msg = (
                f"{path} must have columns {_HOLDINGS_HEADER}, "
                f"got {reader.fieldnames}"
            )
            raise ValueError(
                msg,
            )
        return [
            Holding(symbol=row["symbol"], url=row["url"]) for row in reader
        ]


def write_prices(path: Path, results: list[PriceResult]) -> None:
    """Write holding/price pairs to CSV, one row per holding."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Holding", "GBP Price"])
        for result in results:
            amount = f"{result.price:.4f}" if result.price is not None else ""
            writer.writerow([result.holding.symbol, amount])
