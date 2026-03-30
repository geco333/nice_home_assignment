import re
from playwright.sync_api import Page


def wait_for_page_load(page: Page) -> None:
    page.wait_for_load_state("networkidle")


def parse_balance(text: str) -> float:
    cleaned = re.sub(r"[$,]", "", text)
    return float(cleaned)
