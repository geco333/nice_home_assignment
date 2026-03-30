"""
Negative scenario tests for ParaBank.

1. Login with invalid credentials
2. Register with missing required fields
3. Transfer with invalid / zero amount
4. API – fetch non-existent account (404)
"""

import pytest
import requests
from playwright.sync_api import Page, expect

from src.api.api_client import ApiClient
from src.config.environment import ENV
from src.models.customer import LoginCredentials
from src.pages.login_page import LoginPage
from src.pages.register_page import RegisterPage
from src.pages.transfer_funds_page import TransferFundsPage
from src.utils.data_factory import create_customer_registration, credentials_from


@pytest.mark.negative
class TestNegativeScenarios:

    # ── 1. Login with invalid credentials ─────────────────────

    def test_login_invalid_credentials(self, page: Page):
        login_page = LoginPage(page, ENV.base_url)
        login_page.open()
        login_page.login(LoginCredentials(username="invalid_user", password="wrong_pass"))

        error = login_page.get_error_message()
        assert "error" in error.lower() or "not recognized" in error.lower() or "could not be verified" in error.lower(), (
            f"Expected login error message, got: {error}"
        )

    # ── 2. Register with missing required fields ──────────────

    def test_register_missing_fields(self, page: Page):
        register_page = RegisterPage(page, ENV.base_url)
        register_page.open()

        # Submit the form empty
        page.click(RegisterPage.REGISTER_BTN)
        page.wait_for_load_state("domcontentloaded")

        errors = register_page.get_error_messages()
        assert len(errors) > 0, "Expected validation errors for empty form submission"

        expected_fields = ["First name", "Last name", "Address", "City", "State", "Zip Code", "Username", "Password"]
        for field in expected_fields:
            has_error = any(field.lower() in e.lower() for e in errors)
            assert has_error, f"Expected validation error for '{field}', got errors: {errors}"

    # ── 3. Register with an already existing username ─────────

    def test_register_duplicate_username(self, page: Page):
        customer_data = create_customer_registration()

        register_page = RegisterPage(page, ENV.base_url)
        register_page.open()
        register_page.register(customer_data)

        heading = register_page.get_success_heading()
        assert "Welcome" in heading, "First registration should succeed"

        register_page.open()
        register_page.register(customer_data)

        errors = register_page.get_error_messages()
        assert len(errors) > 0, "Expected error for duplicate username"
        assert any("already exists" in e.lower() or "username" in e.lower() for e in errors), (
            f"Expected 'already exists' error, got: {errors}"
        )

    # ── 4. API – get non-existent account returns error ───────

    def test_api_get_nonexistent_account(self, api_client: ApiClient):
        response = api_client.get("accounts/999999999")

        assert response.status_code in (400, 404, 500), (
            f"Expected error status for non-existent account, got: {response.status_code}"
        )

    # ── 5. API – login with wrong credentials returns error ───

    def test_api_login_invalid_credentials(self, api_client: ApiClient):
        response = api_client.get("login/nonexistent_user_xyz/badpassword")

        assert response.status_code in (400, 401, 403, 404, 500), (
            f"Expected error status for invalid login, got: {response.status_code}"
        )
