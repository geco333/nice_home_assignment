"""
End-to-end banking workflow test.

Scenario:
  1. Register new user (UI)
  2. Login (UI)
  3. Get customer ID (API)
  4. Get existing account (API)
  5. Create new CHECKING account (curl)
  6. Verify new account appears in UI
  7. Transfer money between accounts (UI)
  8. Validate updated balances (API)
  9. Logout
"""

import pytest
from playwright.sync_api import Page, expect

from src.api.account_api import AccountApi
from src.api.customer_api import CustomerApi
from src.config.environment import ENV
from src.models.account import AccountType
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.login_page import LoginPage
from src.pages.register_page import RegisterPage
from src.pages.transfer_funds_page import TransferFundsPage
from src.utils.data_factory import create_customer_registration, credentials_from, random_transfer_amount


@pytest.mark.e2e
class TestBankingWorkflow:
    """Full end-to-end banking workflow validating UI + API consistency."""

    def test_full_banking_flow(
        self,
        page: Page,
        customer_api: CustomerApi,
        account_api: AccountApi,
    ):
        base = ENV.base_url
        customer_data = create_customer_registration()
        credentials = credentials_from(customer_data)

        # ── Step 1: Register new user (UI) ────────────────────────
        register_page = RegisterPage(page, base)
        register_page.open()
        register_page.register(customer_data)

        welcome_heading = register_page.get_success_heading()
        assert "Welcome" in welcome_heading, f"Expected welcome heading, got: {welcome_heading}"

        success_msg = register_page.get_success_message()
        assert "created successfully" in success_msg.lower() or customer_data.username in success_msg, (
            f"Expected registration success message, got: {success_msg}"
        )

        # Registration auto-logs in; log out first so we can test explicit login
        page.locator("a:text('Log Out')").click()
        page.wait_for_load_state("domcontentloaded")

        # ── Step 2: Login (UI) ────────────────────────────────────
        login_page = LoginPage(page, base)
        login_page.open()
        login_page.login(credentials)

        welcome = login_page.get_welcome_message()
        assert "Accounts Overview" in welcome or "Welcome" in welcome, (
            f"Login did not redirect to expected page. Heading: {welcome}"
        )

        # ── Step 3: Get customer ID (API) ─────────────────────────
        customer_id = customer_api.get_customer_id(credentials.username, credentials.password)
        assert isinstance(customer_id, int) and customer_id > 0, (
            f"Expected positive integer customer ID, got: {customer_id}"
        )

        customer = customer_api.get_customer(customer_id)
        assert customer.first_name == customer_data.first_name
        assert customer.last_name == customer_data.last_name

        # ── Step 4: Get existing account (API) ────────────────────
        accounts = account_api.get_customer_accounts(customer_id)
        assert len(accounts) >= 1, "Newly registered user should have at least one account"

        existing_account = accounts[0]
        assert existing_account.customer_id == customer_id
        assert existing_account.id > 0

        existing_account_id = existing_account.id

        # ── Step 5: Create new CHECKING account (curl) ────────────
        new_account = account_api.create_account_via_curl(
            customer_id=customer_id,
            new_account_type=AccountType.CHECKING,
            from_account_id=existing_account_id,
        )
        assert new_account.id > 0, "New account should have a valid ID"
        assert new_account.type == "CHECKING", f"Expected CHECKING, got: {new_account.type}"
        assert new_account.customer_id == customer_id

        new_account_id = new_account.id

        # ── Step 6: Verify new account appears in UI ──────────────
        overview_page = AccountsOverviewPage(page, base)
        overview_page.open()

        account_ids = overview_page.get_account_ids()
        assert str(new_account_id) in account_ids, (
            f"New account {new_account_id} not found in UI. Visible accounts: {account_ids}"
        )

        # ── Step 7: Transfer money between accounts (UI) ──────────
        transfer_amount = random_transfer_amount(min_val=5, max_val=50)

        balance_before_from = account_api.get_account(existing_account_id).balance
        balance_before_to = account_api.get_account(new_account_id).balance

        transfer_page = TransferFundsPage(page, base)
        transfer_page.open()
        transfer_page.transfer(
            amount=str(transfer_amount),
            from_account_id=str(existing_account_id),
            to_account_id=str(new_account_id),
        )

        success_heading = transfer_page.get_success_heading()
        assert "Transfer Complete" in success_heading, (
            f"Expected 'Transfer Complete', got: {success_heading}"
        )

        # ── Step 8: Validate updated balances (API) ───────────────
        updated_from = account_api.get_account(existing_account_id)
        updated_to = account_api.get_account(new_account_id)

        expected_from_balance = balance_before_from - transfer_amount
        expected_to_balance = balance_before_to + transfer_amount

        assert abs(updated_from.balance - expected_from_balance) < 0.01, (
            f"Source balance mismatch: expected {expected_from_balance}, got {updated_from.balance}"
        )
        assert abs(updated_to.balance - expected_to_balance) < 0.01, (
            f"Destination balance mismatch: expected {expected_to_balance}, got {updated_to.balance}"
        )

        # ── Step 9: Logout ────────────────────────────────────────
        page.locator("a:text('Log Out')").click()
        page.wait_for_load_state("domcontentloaded")

        expect(page.locator("input[name='username']")).to_be_visible()
        expect(page.locator("input[name='password']")).to_be_visible()
