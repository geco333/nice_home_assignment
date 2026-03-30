"""
Negative scenario tests for ParaBank, split into UI and API concerns.

Each test is independent and does not rely on shared state.
"""
import logging

import allure
import pytest
from playwright.sync_api import Page

from src.api.api_client import ApiClient
from src.config.environment import ENV
from src.models.customer import LoginCredentials
from src.pages.login_page import LoginPage
from src.pages.register_page import RegisterPage
from src.utils.data_factory import create_customer_registration

logger = logging.getLogger("parabank.negative")


@pytest.mark.negative
@allure.epic("ParaBank Banking")
@allure.feature("UI Negative Scenarios")
class TestNegativeUI:
    """UI-focused negative scenarios."""

    @allure.story("Authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login with invalid credentials shows error")
    def test_login_invalid_credentials(self, page: Page):
        logger.info("🔐 Attempting login with invalid credentials")
        
        with allure.step("Attempt login with wrong username/password"):
            login_page = LoginPage(page, ENV.base_url)
            login_page.open()
            login_page.login(LoginCredentials(username="invalid_user", password="wrong_pass"))

        with allure.step("Verify error message is displayed"):
            error = login_page.get_error_message()
            logger.info("🚫 Error message received: %s", error)
            
            assert "error" in error.lower() or "not recognized" in error.lower() or "could not be verified" in error.lower(), (
                f"Expected login error message, got: {error}"
            )

    @allure.story("Registration")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Register with empty form shows validation errors")
    def test_register_missing_fields(self, page: Page):
        logger.info("📝 Submitting empty registration form")
        with allure.step("Open registration page and submit empty form"):
            register_page = RegisterPage(page, ENV.base_url)
            register_page.open()
            page.click(RegisterPage.REGISTER_BTN)
            page.wait_for_load_state("domcontentloaded")

        with allure.step("Verify validation errors for all required fields"):
            errors = register_page.get_error_messages()
            logger.info("⚠️ Got %d validation error(s): %s", len(errors), errors)
            assert len(errors) > 0, "Expected validation errors for empty form submission"

            expected_fields = ["First name", "Last name", "Address", "City", "State", "Zip Code", "Username",
                               "Password"]
            for field in expected_fields:
                has_error = any(field.lower() in e.lower() for e in errors)
                assert has_error, f"Expected validation error for '{field}', got errors: {errors}"
            logger.info("✅ All %d required fields show validation errors", len(expected_fields))

    @allure.story("Registration")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Register with duplicate username shows error")
    def test_register_duplicate_username(self, page: Page):
        customer_data = create_customer_registration()
        logger.info("👯 Testing duplicate registration for user: %s", customer_data.username)

        with allure.step("Register user for the first time"):
            register_page = RegisterPage(page, ENV.base_url)
            register_page.open()
            register_page.register(customer_data)
            heading = register_page.get_success_heading()
            assert "Welcome" in heading, "First registration should succeed"
            logger.info("✅ First registration succeeded")

        with allure.step("Attempt to register the same username again"):
            register_page.open()
            register_page.register(customer_data)
            logger.info("🔄 Re-submitted same username: %s", customer_data.username)

        with allure.step("Verify duplicate username error"):
            errors = register_page.get_error_messages()
            logger.info("🚫 Duplicate error(s): %s", errors)
            assert len(errors) > 0, "Expected error for duplicate username"
            assert any("already exists" in e.lower() or "username" in e.lower() for e in errors), (
                f"Expected 'already exists' error, got: {errors}"
            )


@pytest.mark.negative
@allure.epic("ParaBank Banking")
@allure.feature("API Negative Scenarios")
class TestNegativeAPI:
    """API-focused negative scenarios."""

    @allure.story("Account Lookup")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET non-existent account returns error status")
    def test_get_nonexistent_account(self, api_client: ApiClient):
        logger.info("👻 Requesting non-existent account ID 999999999")
        with allure.step("GET /accounts/999999999"):
            response = api_client.get("accounts/999999999")

        with allure.step(f"Verify error status code (got {response.status_code})"):
            logger.info("📡 Response status: %d", response.status_code)
            assert response.status_code in (400, 404, 500), (
                f"Expected error status for non-existent account, got: {response.status_code}"
            )

    @allure.story("Authentication")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("API login with invalid credentials returns error status")
    def test_login_invalid_credentials(self, api_client: ApiClient):
        logger.info("🔐 Attempting API login with bogus credentials")
        with allure.step("GET /login/nonexistent_user_xyz/badpassword"):
            response = api_client.get("login/nonexistent_user_xyz/badpassword")

        with allure.step(f"Verify error status code (got {response.status_code})"):
            logger.info("📡 Response status: %d — access denied as expected!", response.status_code)
            assert response.status_code in (400, 401, 403, 404, 500), (
                f"Expected error status for invalid login, got: {response.status_code}"
            )
