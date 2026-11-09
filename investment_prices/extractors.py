"""Per-site price extraction.

Each broker gets its own small class implementing the ``PriceExtractor``
protocol. Two things changed from the original script beyond the class
wrapping:

1. Each extractor separates the *impure* step (querying the DOM) from
   a *pure* ``parse`` staticmethod (turning scraped text into a
   ``Price``). The parse logic is where the real per-site quirks and
   bugs live, and it's now testable with plain strings, no browser
   required.
2. Site selection is done by matching the URL's hostname, via a
   registry dict, instead of ``url[12:15]`` character slicing (which
   silently breaks for any URL that isn't exactly the assumed shape,
   e.g. no leading "www."). Adding a new site now means adding one
   class and one registry entry, rather than editing an if/elif chain
   (open/closed principle).

NOTE: the hostname keywords in ``_EXTRACTORS_BY_HOST_KEYWORD`` below
are inferred from the original ``url[12:15]`` checks ('lon', 'ajb',
'mar', 'hl.') — double-check them against the actual URLs in your
holdings.csv and adjust if needed.
"""
import logging
from decimal import InvalidOperation
from typing import Protocol
from urllib.parse import urlparse

from selenium.common.exceptions import (
    JavascriptException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from .models import Currency, Price
from .parsing import parse_amount

logger = logging.getLogger(__name__)


class UnsupportedSourceError(Exception):
    """Raised when a holding's URL doesn't match any known price source."""


class PriceExtractor(Protocol):
    """Anything that can pull the current price off an already-loaded page."""

    def extract(self, driver: WebDriver) -> Price | None: ...  # noqa: D102


class IWebExtractor:
    """Extracts the current price from an iweb holding page."""

    _XPATH = (
        "//p[contains(@class, 'description__label') and "
        "contains(text(), 'Price')]/following-sibling::*"
    )

    def extract(self, driver: WebDriver) -> Price | None:
        """Extract price element from page."""
        try:
            element = driver.find_element(By.XPATH, self._XPATH)
        except (NoSuchElementException, TimeoutException) as exc:
            logger.warning("iweb: could not locate price element: %s", exc)
            return None
        return self.parse(element.text)

    @staticmethod
    def parse(text: str) -> Price | None:
        """Parse extracted price."""
        try:
            amount = parse_amount(text)
            currency = Currency(text.strip()[-3:])
        except (InvalidOperation, ValueError) as exc:
            logger.warning("iweb: could not parse price %r: %s", text, exc)
            return None
        return Price(amount, currency)


class HLExtractor:
    """Extracts the current price from a Hargreaves Lansdown holding page."""

    _SELECTOR = ".bid.price-divide"

    def extract(self, driver: WebDriver) -> Price | None:
        """Extract price element from page."""
        try:
            text = driver.execute_script( # pyright: ignore[reportUnknownMemberType]
                "return document.querySelector('"
                f"{self._SELECTOR}"
                "').textContent",
            )
        except (JavascriptException, TimeoutException) as exc:
            logger.warning("hl: could not read price element: %s", exc)
            return None
        return self.parse(text)

    @staticmethod
    def parse(text: str) -> Price | None:
        """Parse extracted price."""
        # HL always quotes in pence (GBX).
        try:
            amount = parse_amount(text)
        except InvalidOperation as exc:
            logger.warning("hl: could not parse price %r: %s", text, exc)
            return None
        return Price(amount, Currency.GBX)


class AJBellExtractor:
    """Extracts the current price from an AJ Bell holding page."""

    _SELECTOR = '[data-testid="priceValue"]'

    def extract(self, driver: WebDriver) -> Price | None:
        """Extract price element from page."""
        try:
            text = driver.execute_script( # pyright: ignore[reportUnknownMemberType]
                "return document.querySelector('"
                f"{self._SELECTOR}"
                "').textContent",
            )
        except (JavascriptException, TimeoutException) as exc:
            logger.warning("ajbell: could not read price element: %s", exc)
            return None
        return self.parse(text)

    @staticmethod
    def parse(text: str) -> Price | None:
        """Parse extracted price."""
        text = text.strip()
        if text.startswith("\u00a3"):
            currency = Currency.GBP
        elif text.endswith("p"):
            currency = Currency.GBX
        else:
            logger.warning("ajbell: unrecognised price format %r", text)
            return None
        try:
            amount = parse_amount(text)
        except InvalidOperation as exc:
            logger.warning("ajbell: could not parse price %r: %s", text, exc)
            return None
        return Price(amount, currency)


class LSEExtractor:
    """Extracts the current price from a London Stock Exchange holding page."""

    def extract(self, driver: WebDriver) -> Price | None:
        """Extract price element from page."""
        try:
            currency_label = driver.find_element(
                By.XPATH, "//div[@class='RichTextMultiColumn-labelHolder' and "
                          "starts-with(normalize-space(text()), 'Price GB')]",
            )
            price_element = driver.find_element(
                By.XPATH, "//div[@class='RichTextMultiColumn-labelHolder' and "
                          "starts-with(normalize-space(text()), 'Price GB')]"
                          "/parent::*/following-sibling::*[1]",
            )
        except (NoSuchElementException, TimeoutException) as exc:
            logger.warning("lse: could not locate price elements: %s", exc)
            return None
        return self.parse(price_element.text, currency_label.text)

    @staticmethod
    def parse(price_text: str, currency_text: str) -> Price | None:
        """Parse extracted price."""
        try:
            currency = Currency(currency_text.strip("() ")[-3:])
            amount = parse_amount(price_text)
        except (InvalidOperation, ValueError) as exc:
            logger.warning(
                "lse: could not parse price %r / currency %r: %s",
                price_text, currency_text, exc,
            )
            return None
        return Price(amount, currency)


# Hostname substring -> extractor. Checked in order; first match wins.
_EXTRACTORS_BY_HOST_KEYWORD: dict[str, PriceExtractor] = {
    "londonstockexchange": LSEExtractor(),
    "ajbell": AJBellExtractor(),
    "iweb": IWebExtractor(),
    "hl.co.uk": HLExtractor(),
}


def get_extractor(url: str) -> PriceExtractor:
    """Pick the right extractor for a holding's URL based on its hostname."""
    host = urlparse(url).netloc.lower()
    for keyword, extractor in _EXTRACTORS_BY_HOST_KEYWORD.items():
        if keyword in host:
            return extractor
    msg = f"No extractor registered for host {host!r} ({url})"
    raise UnsupportedSourceError(msg)
