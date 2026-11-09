"""Application orchestrator: fetch each holding's price and persist results."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .currency import CurrencyConverter
from .extractors import UnsupportedSourceError, get_extractor
from .io_utils import read_holdings, write_prices
from .models import GBPAmount, Holding, PriceResult
from .rates import FTExchangeRateProvider

if TYPE_CHECKING:
    from selenium.webdriver.chrome.webdriver import WebDriver

    from .config import Settings

logger = logging.getLogger(__name__)


def fetch_price(
    driver: WebDriver,
    holding: Holding,
    converter: CurrencyConverter,
    max_retries: int,
) -> GBPAmount | None:
    """Fetch and convert a single holding's price, retrying on failure."""
    try:
        extractor = get_extractor(holding.url)
    except UnsupportedSourceError:
        logger.exception("%s: skipping", holding.symbol)
        return None

    for attempt in range(1, max_retries + 1):
        logger.info(
            "Looking up %s (attempt %d/%d)",
            holding.symbol, attempt, max_retries,
        )
        driver.get(holding.url)
        driver.implicitly_wait(2)
        price = extractor.extract(driver)
        if price is not None:
            return converter.to_gbp(price)

    logger.error(
        "Giving up on %s after %d attempts",
        holding.symbol, max_retries,
    )
    return None


def run(driver: WebDriver, settings: Settings) -> list[PriceResult]:
    """Look up and persist the GBP price of every holding in settings."""
    holdings = read_holdings(settings.holdings_path)
    rate = FTExchangeRateProvider(driver).usd_to_gbp_rate()
    converter = CurrencyConverter(usd_gbp_rate=rate)

    results = [
        PriceResult(
            holding,
            fetch_price(driver, holding, converter, settings.max_retries),
        )
        for holding in holdings
    ]
    write_prices(settings.prices_path, results)
    return results
