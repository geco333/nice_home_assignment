"""Shared fixtures for all test modules."""
from typing import Iterator

import pytest
from playwright.sync_api import Page

from src.api.api_client import ApiClient
from src.api.customer_api import CustomerApi
from src.api.account_api import AccountApi
from src.config.environment import ENV


# ── Playwright browser configuration ─────────────────────────

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": ENV.headless,
        "slow_mo": ENV.slow_mo,
    }


# ── API fixtures ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_client():
    client = ApiClient(ENV.api_base_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def customer_api(api_client: ApiClient) -> CustomerApi:
    return CustomerApi(api_client)


@pytest.fixture(scope="session")
def account_api(api_client: ApiClient) -> AccountApi:
    return AccountApi(api_client)


# ── E2E workflow fixtures ─────────────────────────────────────

@pytest.fixture(scope="class")
def shared_page(browser) -> Iterator[Page]:
    """Class-scoped page so the browser session persists across ordered test methods."""
    
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True,
    )
    page = context.new_page()
    
    yield page
    
    context.close()


@pytest.fixture(scope="class")
def shared_context() -> dict:
    """Mutable dict shared across all tests within a class for passing workflow data."""
    
    return {}
