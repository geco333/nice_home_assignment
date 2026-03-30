"""
End-to-end banking workflow tests, split into UI and API concerns.

Each class registers its own user so the classes are independently runnable.
Within each class, tests are ordered sequentially and share state via the
class-scoped ``shared_context`` dict.
"""
import logging

import allure
import pytest
from playwright.sync_api import Page, expect

from src.api.account_api import AccountApi
from src.api.customer_api import CustomerApi
from src.config.environment import ENV
from src.models.account import AccountType
from src.models.customer import CustomerRegistration, LoginCredentials
from src.pages.accounts_overview_page import AccountsOverviewPage
from src.pages.login_page import LoginPage
from src.pages.register_page import RegisterPage
from src.pages.transfer_funds_page import TransferFundsPage
from src.utils.data_factory import create_customer_registration, credentials_from, random_transfer_amount

logger = logging.getLogger("parabank.e2e")


def register_customer(shared_context: dict) -> CustomerRegistration:
    customer_data = create_customer_registration()
    credentials = credentials_from(customer_data)
    
    shared_context["customer_data"] = customer_data
    shared_context["credentials"] = credentials


def setup_accounts(shared_context: dict, customer_api: CustomerApi, account_api: AccountApi) -> None:
    """Fetch customer ID, existing account, and create a new CHECKING account. Stores results in shared_context."""
    credentials = shared_context["credentials"]
    customer_id = customer_api.get_customer_id(credentials.username, credentials.password)
    accounts = account_api.get_customer_accounts(customer_id)
    existing_account_id = accounts[0].id
    new_account = account_api.create_account_via_curl(
        customer_id=customer_id,
        new_account_type=AccountType.CHECKING,
        from_account_id=existing_account_id,
    )

    shared_context["customer_id"] = customer_id
    shared_context["existing_account_id"] = existing_account_id
    shared_context["new_account_id"] = new_account.id

    logger.info("🔧 Setup: accounts ready — existing=%d, new=%d", existing_account_id, new_account.id)


# ── UI tests ──────────────────────────────────────────────────

@pytest.mark.e2e
@allure.epic("ParaBank Banking")
@allure.feature("UI Banking Workflow")
class TestBankingUI:
    """UI-focused banking workflow: register, login, verify account, transfer, logout."""

    @allure.story("User Registration")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Register a new customer")
    def test_register_new_user(self, shared_page: Page, shared_context: dict):
        customer_data = create_customer_registration()
        shared_context["customer_data"] = customer_data
        shared_context["credentials"] = credentials_from(customer_data)
        
        logger.info("📝 Registering new user: %s", customer_data.username)

        with allure.step("Open registration page and fill form"):
            register_page = RegisterPage(shared_page, ENV.base_url)
            register_page.open()
            register_page.register(customer_data)
          
            logger.debug("📋 Registration form submitted for %s %s",
                         customer_data.first_name, customer_data.last_name)

        with allure.step("Verify welcome heading"):
            welcome_heading = register_page.get_success_heading()
         
            logger.info("🎉 Welcome heading received: %s", welcome_heading)

            assert "Welcome" in welcome_heading, f"Expected welcome heading, got: {welcome_heading}"

        with allure.step("Verify success message"):
            success_msg = register_page.get_success_message()
         
            logger.info("✅ Registration success message: %s", success_msg)

            assert "created successfully" in success_msg.lower() or customer_data.username in success_msg, (
                f"Expected registration success message, got: {success_msg}"
            )

        with allure.step("Log out after auto-login"):
            shared_page.locator("a:text('Log Out')").click()
            shared_page.wait_for_load_state("domcontentloaded")
        
            logger.info("🚪 Logged out after auto-login")

    @allure.story("User Login")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Login with registered credentials")
    def test_login(self, shared_page: Page, shared_context: dict, customer_api: CustomerApi):
        logger.info("🏦 Fetching customer data ...")

        if not shared_context.get('credentials'):
            register_customer(shared_context)
            
            with allure.step("Register a new user via API"):
                customer_api.register(shared_context['customer_data'], ENV.base_url)

        credentials = shared_context['credentials']

        logger.info("🔑 Logging in as '%s'", credentials.username)

        with allure.step(f"Login as '{credentials.username}'"):
            login_page = LoginPage(shared_page, ENV.base_url)
            login_page.open()
            login_page.login(credentials)

        with allure.step("Verify successful login redirect"):
            welcome = login_page.get_welcome_message()
            logger.info("👋 Login successful — page heading: %s", welcome)

            assert "Accounts Overview" in welcome or "Welcome" in welcome, (
                f"Login did not redirect to expected page. Heading: {welcome}"
            )

    @allure.story("Account Verification")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify newly created account appears in UI")
    def test_verify_new_account_in_ui(self,
                                      shared_page: Page,
                                      shared_context: dict,
                                      customer_api: CustomerApi,
                                      account_api: AccountApi):
        logger.info("🏦 Fetching customer data and creating new checking account")

        if not shared_context.get('credentials'):
            register_customer(shared_context)

            with allure.step("Register a new user via API"):
                customer_api.register(shared_context['customer_data'], ENV.base_url)

            with allure.step("Login via UI"):
                login_page = LoginPage(shared_page, ENV.base_url)
                login_page.open()
                login_page.login(shared_context['credentials'])
                logger.info("🔑 Logged in as '%s'", shared_context['credentials'].username)

        credentials = shared_context['credentials']

        with allure.step("Fetch customer and account data via API"):
            customer_id = customer_api.get_customer_id(
                credentials.username, credentials.password)
            accounts = account_api.get_customer_accounts(customer_id)
            existing_account_id = accounts[0].id

            logger.info("🆔 Customer ID: %d | Existing account: %d",
                        customer_id, existing_account_id)

        with allure.step("Create new CHECKING account via curl"):
            new_account = account_api.create_account_via_curl(
                customer_id=customer_id,
                new_account_type=AccountType.CHECKING,
                from_account_id=existing_account_id,
            )
            logger.info("🆕 New CHECKING account created: %d", new_account.id)

        shared_context["customer_id"] = customer_id
        shared_context["existing_account_id"] = existing_account_id
        shared_context["new_account_id"] = new_account.id

        with allure.step(f"Verify account {new_account.id} is visible in Accounts Overview"):
            overview_page = AccountsOverviewPage(shared_page, ENV.base_url)
            overview_page.open()
            account_ids = overview_page.get_account_ids()

            logger.info("👀 Visible accounts in UI: %s", account_ids)

            assert str(new_account.id) in account_ids, (
                f"New account {new_account.id} not found in UI. Visible accounts: {account_ids}"
            )
            logger.info("✅ Account %d verified in UI", new_account.id)

    @allure.story("Fund Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Transfer money between accounts")
    def test_transfer_funds(self, shared_page: Page, shared_context: dict,
                            customer_api: CustomerApi, account_api: AccountApi):
        if not shared_context.get('credentials'):
            register_customer(shared_context)

            with allure.step("Register a new user via API"):
                customer_api.register(shared_context['customer_data'], ENV.base_url)

            with allure.step("Login"):
                login_page = LoginPage(shared_page, ENV.base_url)
                login_page.open()
                login_page.login(shared_context['credentials'])
                logger.info("🔑 Logged in as '%s'", shared_context['credentials'].username)

        if "existing_account_id" not in shared_context or "new_account_id" not in shared_context:
            with allure.step("Setup accounts via API"):
                setup_accounts(shared_context, customer_api, account_api)

        existing_account_id = shared_context["existing_account_id"]
        new_account_id = shared_context["new_account_id"]
        transfer_amount = random_transfer_amount(min_val=5, max_val=50)
        shared_context["transfer_amount"] = transfer_amount

        logger.info("💸 Transferring $%s from account %d → %d",
                    transfer_amount, existing_account_id, new_account_id)

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
            logger.info("🎯 Transfer result: %s", success_heading)

            assert "Transfer Complete" in success_heading, (
                f"Expected 'Transfer Complete', got: {success_heading}"
            )

    @allure.story("User Logout")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Logout and verify login form is displayed")
    def test_logout(self, shared_page: Page):
        logger.info("🚪 Logging out...")

        with allure.step("Click Log Out"):
            shared_page.locator("a:text('Log Out')").click()
            shared_page.wait_for_load_state("domcontentloaded")

        with allure.step("Verify login form is visible"):
            expect(shared_page.locator(
                "input[name='username']")).to_be_visible()
            expect(shared_page.locator(
                "input[name='password']")).to_be_visible()
            logger.info("👋 Logged out — login form is visible again")


# ── API tests ─────────────────────────────────────────────────

@pytest.mark.e2e
@pytest.mark.usefixtures("shared_page")
@allure.epic("ParaBank Banking")
@allure.feature("API Banking Workflow")
class TestBankingAPI:
    """API-focused banking workflow: customer lookup, account creation (curl), balance validation."""

    @allure.story("User Registration")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Register user via API (setup for API tests)")
    def test_register_user(self, shared_context: dict, customer_api: CustomerApi):
        customer_data = create_customer_registration()
        shared_context["customer_data"] = customer_data
        shared_context["credentials"] = credentials_from(customer_data)
        logger.info("🛠️ Registering API test user: %s", customer_data.username)

        with allure.step("Register new user via API (HTTP form POST)"):
            customer_api.register(customer_data, ENV.base_url)

        with allure.step("Verify user can login via API"):
            customer_id = customer_api.get_customer_id(
                customer_data.username, customer_data.password)
                
            assert customer_id > 0, f"Expected valid customer ID after registration, got: {customer_id}"

            logger.info("✅ User registered — customer ID: %d", customer_id)

    @allure.story("Customer Data")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Retrieve customer ID via API login")
    def test_get_customer_id(self, shared_context: dict, customer_api: CustomerApi):
        credentials = shared_context["credentials"]
        logger.info("🔍 Looking up customer ID for '%s' via API",
                    credentials.username)

        with allure.step(f"GET /login/{credentials.username}/****"):
            customer_id = customer_api.get_customer_id(
                credentials.username, credentials.password)

        with allure.step(f"Validate customer ID: {customer_id}"):
            assert isinstance(customer_id, int) and customer_id > 0, (
                f"Expected positive integer customer ID, got: {customer_id}"
            )
            logger.info("🆔 Customer ID retrieved: %d", customer_id)

        shared_context["customer_id"] = customer_id

    @allure.story("Customer Data")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Validate customer details match registration data")
    def test_validate_customer_details(self, shared_context: dict, customer_api: CustomerApi):
        customer_data = shared_context["customer_data"]
        customer_id = shared_context["customer_id"]
       
        logger.info("🧾 Validating customer details for ID %d", customer_id)

        with allure.step(f"GET /customers/{customer_id}"):
            customer = customer_api.get_customer(customer_id)
          
            logger.debug("📦 API response: %s %s, %s, %s",
                         customer.first_name, customer.last_name,
                         customer.address.city, customer.address.state)

        with allure.step("Assert all fields match registration input"):
            assert customer.first_name == customer_data.first_name
            assert customer.last_name == customer_data.last_name
            assert customer.address.street == customer_data.address.street
            assert customer.address.city == customer_data.address.city
            assert customer.address.state == customer_data.address.state
            assert customer.address.zip_code == customer_data.address.zip_code
        
            logger.info("✅ All customer fields match registration data")

    @allure.story("Account Management")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Retrieve existing account for customer")
    def test_get_existing_account(self, shared_context: dict, account_api: AccountApi):
        customer_id = shared_context["customer_id"]
        logger.info("🏦 Fetching accounts for customer %d", customer_id)

        with allure.step(f"GET /customers/{customer_id}/accounts"):
            accounts = account_api.get_customer_accounts(customer_id)
         
            logger.info("📊 Found %d account(s)", len(accounts))

        with allure.step("Validate at least one account exists"):
            assert len(
                accounts) >= 1, "Newly registered user should have at least one account"
          
            existing_account = accounts[0]
         
            assert existing_account.customer_id == customer_id
            assert existing_account.id > 0
         
            logger.info("💳 Using existing account: %d (balance: $%.2f)",
                        existing_account.id, existing_account.balance)

        shared_context["existing_account_id"] = existing_account.id

    @allure.story("Account Management")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create new CHECKING account via curl")
    def test_create_checking_account_via_curl(self, shared_context: dict, account_api: AccountApi):
        customer_id = shared_context["customer_id"]
        existing_account_id = shared_context["existing_account_id"]
     
        logger.info(
            "🚀 Creating new CHECKING account via curl for customer %d", customer_id)

        with allure.step("POST /createAccount via curl subprocess"):
            new_account = account_api.create_account_via_curl(
                customer_id=customer_id,
                new_account_type=AccountType.CHECKING,
                from_account_id=existing_account_id,
            )

        with allure.step(f"Validate new account {new_account.id}"):
            assert new_account.id > 0, "New account should have a valid ID"
            assert new_account.type == "CHECKING", f"Expected CHECKING, got: {new_account.type}"
            assert new_account.customer_id == customer_id
         
            logger.info("🆕 CHECKING account created: %d (type: %s)",
                        new_account.id, new_account.type)

        shared_context["new_account_id"] = new_account.id

    @allure.story("Fund Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Transfer funds via API and validate balances")
    def test_transfer_and_validate_balances(self, shared_context: dict, account_api: AccountApi):
        existing_account_id = shared_context["existing_account_id"]
        new_account_id = shared_context["new_account_id"]
        transfer_amount = random_transfer_amount(min_val=5, max_val=50)

        logger.info("💰 API transfer: $%s from account %d → %d",
                    transfer_amount, existing_account_id, new_account_id)

        with allure.step("Record balances before transfer"):
            balance_before_from = account_api.get_account(
                existing_account_id).balance
            balance_before_to = account_api.get_account(new_account_id).balance

            logger.info("📊 Balances before — source: $%.2f | dest: $%.2f",
                        balance_before_from, balance_before_to)

        with allure.step(f"POST /transfer ${transfer_amount} from {existing_account_id} to {new_account_id}"):
            transfer_result = account_api.transfer_funds(
                existing_account_id, new_account_id, transfer_amount)

            assert transfer_result["status_code"] == 200, (
                f"Transfer API failed with status {transfer_result['status_code']}"
            )

            logger.info("🔄 Transfer API returned status %d",
                        transfer_result["status_code"])

        with allure.step("Validate updated balances"):
            updated_from = account_api.get_account(existing_account_id)
            updated_to = account_api.get_account(new_account_id)

            expected_from_balance = balance_before_from - transfer_amount
            expected_to_balance = balance_before_to + transfer_amount

            logger.info("📊 Balances after  — source: $%.2f (expected $%.2f) | dest: $%.2f (expected $%.2f)",
                        updated_from.balance, expected_from_balance,
                        updated_to.balance, expected_to_balance)

            assert abs(updated_from.balance - expected_from_balance) < 0.01, (
                f"Source balance mismatch: expected {expected_from_balance}, got {updated_from.balance}"
            )
            assert abs(updated_to.balance - expected_to_balance) < 0.01, (
                f"Destination balance mismatch: expected {expected_to_balance}, got {updated_to.balance}"
            )

            logger.info("✅ Balances validated — transfer math checks out!")
