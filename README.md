# investment-prices

Fetches the current price of each holding in `holdings.csv` from its
broker's website and writes GBP prices to `prices.csv`.

## Layout

```
investment_prices/
    models.py       Currency, Price, Holding, PriceResult — plain immutable value objects
    parsing.py      pure regex-based amount extraction, shared by all extractors
    currency.py     CurrencyConverter — pure GBX/USD -> GBP conversion (rate injected)
    rates.py        FTExchangeRateProvider — the one concrete (Selenium) rate source
    extractors.py   one class per broker site + a hostname -> extractor registry
    browser.py      chrome_driver() context manager
    io_utils.py     read_holdings / write_prices (stdlib csv, no pandas)
    config.py       Settings, built from CLI args
    app.py          orchestration: fetch_price (with bounded retries) + run
    __main__.py     CLI entry point
tests/               unit tests for everything except the Selenium calls themselves
```

## Usage

```bash
pip install -e .
python -m investment_prices --holdings holdings.csv --output prices.csv
```
