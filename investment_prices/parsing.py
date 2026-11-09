"""Pure helpers for pulling a numeric amount out of scraped price text.

Kept free of Selenium and logging so it can be unit tested with plain
strings.
"""
import re
from decimal import Decimal, InvalidOperation

_NUMBER_PATTERN = re.compile(r"[\d,]*\d(?:\.\d+)?")


def parse_amount(text: str) -> Decimal:
    """Extract the numeric amount from a string such as '1,234.50 GBP'.

    Raises InvalidOperation if no number can be found, so callers can
    handle it alongside the ValueError/InvalidOperation cases Decimal
    itself raises.
    """
    match = _NUMBER_PATTERN.search(text)
    if match is None:
        msg = f"No numeric amount found in {text!r}"
        raise InvalidOperation(msg)
    return Decimal(match.group().replace(",", ""))
