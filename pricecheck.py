#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 10:33:46 2024

@author: Jason Shiers

Investment price checker
------------------------
Fetches the current investment price of a list of holdings using specified URLs
and saves them to a CSV file

Requires holdings.csv, a csv file of 'symbol', 'url'
Outputs prices.csv, as csv file of 'Holding' (='symbol'), 'GBP Price'
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class GBP_Price(float):
    """ Unit price of a holding in GBP """
    def __new__(cls, value, currency='GBP'):
        value = float(value)
        if currency == 'GBP':
            pass
        elif currency == 'GBX':
            value *= 0.01
        else:
            raise NotImplementedError(f"Currency {currency} not supported")
        return float.__new__(cls, value)

    def __str__(self, format_spec=".4g"):
        return f"£{self:{format_spec}}"


def setup_driver() -> WebDriver:
    """ Instantiate Selenium Chromium Webdriver """
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--incognito")
    options.add_argument("--disable-plugins-discovery")

    driver = webdriver.Chrome(service=Service('/snap/bin/chromium.chromedriver',
                                              options=options))
    return driver


def get_price_from_iweb(driver: WebDriver) -> GBP_Price | None:
    """ Extracts current market price from iweb webpage
        driver: WebDriver object pre-loaded with a webpage using driver.get(url)
    """
    try:
        price_label = driver.find_element(
            By.XPATH, "//p[contains(@class, 'description__label') "
                      "and contains(text(), 'Price')]")
        element = price_label.find_element(By.XPATH, "./following-sibling::*")
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error getting price: {e}")
        return None

    val = GBP_Price(element.text.replace(',', '')[:8], 'GBX')
    return val


def get_price_from_lse(driver: WebDriver) -> GBP_Price | None:
    """ Extracts current market price from LSE webpage
        driver: WebDriver object pre-loaded with a webpage using driver.get(url)
    """
    # Get the currency label to convert from GBX if required
    try:
        clbl = driver.find_element(
            By.XPATH, '//div[contains(@class, "currency-label")]')
        currency = clbl.text[-5:].strip('()')

        element = driver.find_element(By.XPATH, '//span[@class="price-tag"]')
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error getting price: {e}")
        return None

    val = GBP_Price(element.text.replace(',', '')[:8], currency)
    return val


def main() -> None:
    """ Main function """
    # Read holdings as csv of symbol, url
    holdings = pd.read_csv('holdings.csv')

    # Start web driver
    driver = setup_driver()

    # Loop over holdings and build list list of prices
    prices = []
    for _, holding in holdings.iterrows():
        print(f'Looking up {holding.symbol}')
        driver.get(holding.url)
        driver.implicitly_wait(2)

        # Use url to determine how to process webpage
        if holding.url[12:15] == 'lon':
            val = get_price_from_lse(driver)
        elif holding.url[12:15] == 'mar':
            val = get_price_from_iweb(driver)
        else:
            raise NotImplementedError("URL not supported")
        prices.append((holding.symbol, val))

    # Convert to DataFrame and save as csv
    df = pd.DataFrame(prices, columns=('Holding', 'GBP Price'))
    df.to_csv('prices.csv')
    print(df)


if __name__ == "__main__":
    # Start web driver
    driver = setup_driver()
    try:
        main()
    finally:
        # Shut down web driver
        driver.quit()
