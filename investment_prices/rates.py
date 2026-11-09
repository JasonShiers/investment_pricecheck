"""Concrete exchange-rate provider(s) that need a live browser.

Split out from currency.py so that module stays free of Selenium and
fully unit-testable; this one is exercised in an integration test (or
manually) rather than a pure unit test.
"""
from dataclasses import dataclass
from decimal import Decimal

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


@dataclass(frozen=True, slots=True)
class FTExchangeRateProvider:
    """Fetches the live USD -> GBP rate from the FT markets page."""

    driver: WebDriver
    url: str = "https://markets.ft.com/data/currencies/tearsheet/summary?s=usdgbp"

    def usd_to_gbp_rate(self) -> Decimal:
        """Fetch USD to GBP exchange rate."""
        self.driver.get(self.url)
        self.driver.implicitly_wait(2)
        element = self.driver.find_element(
            By.CSS_SELECTOR, ".mod-ui-data-list__value",
        )
        return Decimal(element.text)
