"""Page Object for the ParaBank customer lookup (forgot login) page."""
from src.pages.base_page import BasePage


class ForgotLoginPage(BasePage):
    """Encapsulates interactions with the ParaBank customer lookup form.

    Used when a customer has forgotten their login credentials and needs
    to recover them by providing personal information.
    """

    PATH = "lookup.htm"

    # Form fields
    FIRST_NAME = "#firstName"
    LAST_NAME = "#lastName"
    ADDRESS = "#address\\.street"
    CITY = "#address\\.city"
    STATE = "#address\\.state"
    ZIP_CODE = "#address\\.zipCode"
    SSN = "#ssn"
    FIND_BTN = "input[value='Find My Login Info']"

    # Result
    SUCCESS_HEADING = "#rightPanel h1"
    USERNAME_RESULT = "#rightPanel p:has-text('Username')"
    PASSWORD_RESULT = "#rightPanel p:has-text('Password')"

    # Error
    ERROR_MESSAGES = "span.error"

    def open(self) -> "ForgotLoginPage":
        """Navigate to the customer lookup page.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        return self

    def lookup(
        self,
        first_name: str,
        last_name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        ssn: str,
    ) -> None:
        """Fill and submit the customer lookup form.

        :param first_name: Customer's first name.
        :param last_name: Customer's last name.
        :param address: Customer's street address.
        :param city: Customer's city.
        :param state: Customer's state.
        :param zip_code: Customer's zip code.
        :param ssn: Customer's Social Security Number.
        """
        self.page.fill(self.FIRST_NAME, first_name)
        self.page.fill(self.LAST_NAME, last_name)
        self.page.fill(self.ADDRESS, address)
        self.page.fill(self.CITY, city)
        self.page.fill(self.STATE, state)
        self.page.fill(self.ZIP_CODE, zip_code)
        self.page.fill(self.SSN, ssn)

        self.page.click(self.FIND_BTN)
        self.page.wait_for_load_state("domcontentloaded")

    def get_success_heading(self) -> str:
        """Return the heading shown after a successful lookup."""
        return self.page.locator(self.SUCCESS_HEADING).inner_text()

    def get_error_messages(self) -> list[str]:
        """Return all validation error messages displayed on the form.

        :returns: List of error strings; empty if no errors are shown.
        """
        return self.page.locator(self.ERROR_MESSAGES).all_inner_texts()
