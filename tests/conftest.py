"""Shared fixtures for all test modules."""

import pytest
from playwright.sync_api import Page

from src.api.api_client import ApiClient
from src.api.customer_api import CustomerApi
from src.api.account_api import AccountApi
from src.config.environment import ENV
from src.pages.register_page import RegisterPage
from src.pages.login_page import LoginPage
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.open_account_page import OpenAccountPage
from src.pages.transfer_funds_page import TransferFundsPage


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


# ── Page-object fixtures ─────────────────────────────────────

@pytest.fixture()
def register_page(page: Page) -> RegisterPage:
    return RegisterPage(page, ENV.base_url)


@pytest.fixture()
def login_page(page: Page) -> LoginPage:
    return LoginPage(page, ENV.base_url)


@pytest.fixture()
def accounts_overview_page(page: Page) -> AccountsOverviewPage:
    return AccountsOverviewPage(page, ENV.base_url)


@pytest.fixture()
def open_account_page(page: Page) -> OpenAccountPage:
    return OpenAccountPage(page, ENV.base_url)


@pytest.fixture()
def transfer_funds_page(page: Page) -> TransferFundsPage:
    return TransferFundsPage(page, ENV.base_url)
