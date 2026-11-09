"""Selenium Chrome WebDriver lifecycle management."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if TYPE_CHECKING:
    from collections.abc import Generator

    from selenium.webdriver.chrome.webdriver import WebDriver

_CHROME_ARGS = (
    "--disable-extensions",
    "--incognito",
    "--disable-plugins-discovery",
)


def _build_options() -> Options:
    options = Options()
    for arg in _CHROME_ARGS:
        options.add_argument(arg)
    return options


@contextmanager
def chrome_driver() -> Generator[WebDriver]:
    """Yield a configured Chrome driver, guaranteeing it is quit afterwards."""
    driver = webdriver.Chrome(options=_build_options())
    try:
        yield driver
    finally:
        driver.quit()
