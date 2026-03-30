"""Page Object for the ParaBank login page."""
from src.models.customer import LoginCredentials
from src.pages.base_page import BasePage


class LoginPage(BasePage):
    """Encapsulates interactions with the ParaBank login form."""

    PATH = "index.htm"

    USERNAME = "input[name='username']"
    PASSWORD = "input[name='password']"
    LOGIN_BTN = "input[value='Log In']"
    ERROR_MESSAGE = "#rightPanel p.error"
    WELCOME_MESSAGE = "#rightPanel h1.title:first-of-type"

    def open(self) -> "LoginPage":
        """Navigate to the login page.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        return self

    def login(self, credentials: LoginCredentials) -> None:
        """Fill and submit the login form.

        :param credentials: LoginCredentials with username and password.
        """
        self.page.fill(self.USERNAME, credentials.username)
        self.page.fill(self.PASSWORD, credentials.password)
        self.page.click(self.LOGIN_BTN)
        self.page.wait_for_load_state("domcontentloaded")

    def get_error_message(self) -> str:
        """Return the login error message (e.g. 'The username and password could not be verified.')."""
        return self.page.locator(self.ERROR_MESSAGE).inner_text()

    def get_welcome_message(self) -> str:
        """Return the first heading in the right panel after login (e.g. 'Accounts Overview')."""
        return self.page.locator("#rightPanel h1").first.inner_text()

    def is_logged_in(self) -> bool:
        """Check whether the welcome heading is visible, indicating a logged-in session."""
        return self.page.locator(self.WELCOME_MESSAGE).is_visible()
