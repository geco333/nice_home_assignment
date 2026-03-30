"""
End-to-end banking workflow tests, split into UI and API concerns.

Each class registers its own user so the classes are independently runnable.
Within each class, tests are ordered sequentially and share state via the
class-scoped ``state`` fixture.
"""

import allure
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
@allure.epic("ParaBank Banking")
@allure.feature("UI Banking Workflow")
class TestBankingUI:
    """UI-focused banking workflow: register, login, verify account, transfer, logout."""

    @allure.story("User Registration")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Register a new user via UI")
    def test_register_new_user(self, shared_page: Page, state: dict):
        base = ENV.base_url
        customer_data = create_customer_registration()
        state["customer_data"] = customer_data
        state["credentials"] = credentials_from(customer_data)

        with allure.step("Open registration page and fill form"):
            register_page = RegisterPage(shared_page, base)
            register_page.open()
            register_page.register(customer_data)

        with allure.step("Verify welcome heading"):
            welcome_heading = register_page.get_success_heading()
            assert "Welcome" in welcome_heading, f"Expected welcome heading, got: {welcome_heading}"

        with allure.step("Verify success message"):
            success_msg = register_page.get_success_message()
            assert "created successfully" in success_msg.lower() or customer_data.username in success_msg, (
                f"Expected registration success message, got: {success_msg}"
            )

        with allure.step("Log out after auto-login"):
            shared_page.locator("a:text('Log Out')").click()
            shared_page.wait_for_load_state("domcontentloaded")

    @allure.story("User Login")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Login with registered credentials")
    def test_login(self, shared_page: Page, state: dict):
        credentials = state["credentials"]

        with allure.step(f"Login as '{credentials.username}'"):
            login_page = LoginPage(shared_page, ENV.base_url)
            login_page.open()
            login_page.login(credentials)

        with allure.step("Verify successful login redirect"):
            welcome = login_page.get_welcome_message()
            assert "Accounts Overview" in welcome or "Welcome" in welcome, (
                f"Login did not redirect to expected page. Heading: {welcome}"
            )

    @allure.story("Account Verification")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify newly created account appears in UI")
    def test_verify_new_account_in_ui(
        self,
        shared_page: Page,
        state: dict,
        customer_api: CustomerApi,
        account_api: AccountApi,
    ):
        credentials = state["credentials"]

        with allure.step("Fetch customer and account data via API"):
            customer_id = customer_api.get_customer_id(credentials.username, credentials.password)
            accounts = account_api.get_customer_accounts(customer_id)
            existing_account_id = accounts[0].id

        with allure.step("Create new CHECKING account via curl"):
            new_account = account_api.create_account_via_curl(
                customer_id=customer_id,
                new_account_type=AccountType.CHECKING,
                from_account_id=existing_account_id,
            )

        state["customer_id"] = customer_id
        state["existing_account_id"] = existing_account_id
        state["new_account_id"] = new_account.id

        with allure.step(f"Verify account {new_account.id} is visible in Accounts Overview"):
            overview_page = AccountsOverviewPage(shared_page, ENV.base_url)
            overview_page.open()
            account_ids = overview_page.get_account_ids()
            assert str(new_account.id) in account_ids, (
                f"New account {new_account.id} not found in UI. Visible accounts: {account_ids}"
            )

    @allure.story("Fund Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Transfer money between accounts via UI")
    def test_transfer_funds(self, shared_page: Page, state: dict):
        existing_account_id = state["existing_account_id"]
        new_account_id = state["new_account_id"]
        transfer_amount = random_transfer_amount(min_val=5, max_val=50)
        state["transfer_amount"] = transfer_amount

        with allure.step(f"Transfer ${transfer_amount} from {existing_account_id} to {new_account_id}"):
            transfer_page = TransferFundsPage(shared_page, ENV.base_url)
            transfer_page.open()
            transfer_page.transfer(
                amount=str(transfer_amount),
                from_account_id=str(existing_account_id),
                to_account_id=str(new_account_id),
            )

        with allure.step("Verify 'Transfer Complete' confirmation"):
            success_heading = transfer_page.get_success_heading()
            assert "Transfer Complete" in success_heading, (
                f"Expected 'Transfer Complete', got: {success_heading}"
            )

    @allure.story("User Logout")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Logout and verify login form is displayed")
    def test_logout(self, shared_page: Page):
        with allure.step("Click Log Out"):
            shared_page.locator("a:text('Log Out')").click()
            shared_page.wait_for_load_state("domcontentloaded")

        with allure.step("Verify login form is visible"):
            expect(shared_page.locator("input[name='username']")).to_be_visible()
            expect(shared_page.locator("input[name='password']")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.usefixtures("shared_page")
@allure.epic("ParaBank Banking")
@allure.feature("API Banking Workflow")
class TestBankingAPI:
    """API-focused banking workflow: customer lookup, account creation (curl), balance validation."""

    @allure.story("User Registration")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Register user via UI (setup for API tests)")
    def test_register_user_setup(self, shared_page: Page, state: dict):
        customer_data = create_customer_registration()
        state["customer_data"] = customer_data
        state["credentials"] = credentials_from(customer_data)

        with allure.step("Register new user via UI"):
            register_page = RegisterPage(shared_page, ENV.base_url)
            register_page.open()
            register_page.register(customer_data)

        with allure.step("Verify registration succeeded"):
            assert "Welcome" in register_page.get_success_heading()

    @allure.story("Customer Data")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Retrieve customer ID via API login")
    def test_get_customer_id(self, state: dict, customer_api: CustomerApi):
        credentials = state["credentials"]

        with allure.step(f"GET /login/{credentials.username}/****"):
            customer_id = customer_api.get_customer_id(credentials.username, credentials.password)

        with allure.step(f"Validate customer ID: {customer_id}"):
            assert isinstance(customer_id, int) and customer_id > 0, (
                f"Expected positive integer customer ID, got: {customer_id}"
            )

        state["customer_id"] = customer_id

    @allure.story("Customer Data")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Validate customer details match registration data")
    def test_validate_customer_details(self, state: dict, customer_api: CustomerApi):
        customer_data = state["customer_data"]

        with allure.step(f"GET /customers/{state['customer_id']}"):
            customer = customer_api.get_customer(state["customer_id"])

        with allure.step("Assert all fields match registration input"):
            assert customer.first_name == customer_data.first_name
            assert customer.last_name == customer_data.last_name
            assert customer.address.street == customer_data.address.street
            assert customer.address.city == customer_data.address.city
            assert customer.address.state == customer_data.address.state
            assert customer.address.zip_code == customer_data.address.zip_code

    @allure.story("Account Management")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Retrieve existing account for customer")
    def test_get_existing_account(self, state: dict, account_api: AccountApi):
        customer_id = state["customer_id"]

        with allure.step(f"GET /customers/{customer_id}/accounts"):
            accounts = account_api.get_customer_accounts(customer_id)

        with allure.step("Validate at least one account exists"):
            assert len(accounts) >= 1, "Newly registered user should have at least one account"
            existing_account = accounts[0]
            assert existing_account.customer_id == customer_id
            assert existing_account.id > 0

        state["existing_account_id"] = existing_account.id

    @allure.story("Account Management")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create new CHECKING account via curl")
    def test_create_checking_account_via_curl(self, state: dict, account_api: AccountApi):
        with allure.step("POST /createAccount via curl subprocess"):
            new_account = account_api.create_account_via_curl(
                customer_id=state["customer_id"],
                new_account_type=AccountType.CHECKING,
                from_account_id=state["existing_account_id"],
            )

        with allure.step(f"Validate new account {new_account.id}"):
            assert new_account.id > 0, "New account should have a valid ID"
            assert new_account.type == "CHECKING", f"Expected CHECKING, got: {new_account.type}"
            assert new_account.customer_id == state["customer_id"]

        state["new_account_id"] = new_account.id

    @allure.story("Fund Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Transfer funds via API and validate balances")
    def test_transfer_and_validate_balances(self, state: dict, account_api: AccountApi):
        existing_account_id = state["existing_account_id"]
        new_account_id = state["new_account_id"]
        transfer_amount = random_transfer_amount(min_val=5, max_val=50)

        with allure.step("Record balances before transfer"):
            balance_before_from = account_api.get_account(existing_account_id).balance
            balance_before_to = account_api.get_account(new_account_id).balance

        with allure.step(f"POST /transfer ${transfer_amount} from {existing_account_id} to {new_account_id}"):
            transfer_result = account_api.transfer_funds(existing_account_id, new_account_id, transfer_amount)
            assert transfer_result["status_code"] == 200, (
                f"Transfer API failed with status {transfer_result['status_code']}"
            )

        with allure.step("Validate updated balances"):
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
