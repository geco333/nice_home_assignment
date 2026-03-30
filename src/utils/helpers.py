"""Stateless utility functions shared across the framework."""
import re
from playwright.sync_api import Page


def wait_for_page_load(page: Page) -> None:
    """Block until the page reaches the ``networkidle`` load state.

    :param page: Playwright Page instance.
    """
    page.wait_for_load_state("networkidle")


def parse_balance(text: str) -> float:
    """Parse a currency string (e.g. ``'$1,234.56'``) into a float.

    Strips dollar signs and commas before converting.

    :param text: Raw balance text from the UI.
    :returns: Numeric balance value.
    """
    cleaned = re.sub(r"[$,]", "", text)
    return float(cleaned)
