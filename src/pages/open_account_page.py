"""Page Object for the ParaBank open-new-account page."""
from src.models.account import AccountType
from src.pages.base_page import BasePage


class OpenAccountPage(BasePage):
    """Encapsulates interactions with the ParaBank new-account creation form."""

    PATH = "openaccount.htm"

    ACCOUNT_TYPE_SELECT = "#type"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    OPEN_ACCOUNT_BTN = "input[value='Open New Account']"
    NEW_ACCOUNT_ID = "#newAccountId"
    SUCCESS_MESSAGE = "#rightPanel h1"

    def open(self) -> "OpenAccountPage":
        """Navigate to the open-account page and wait for dropdowns to load.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        self.page.wait_for_selector(self.FROM_ACCOUNT_SELECT, timeout=10000)
        return self

    def create_account(self, account_type: AccountType, from_account_id: str | None = None) -> str:
        """Create a new account and return the newly assigned account ID.

        :param account_type: Type of account to create (CHECKING or SAVINGS).
        :param from_account_id: Optional source account to fund the new account from.
        :returns: The new account ID as a string.
        """
        self.page.select_option(self.ACCOUNT_TYPE_SELECT, str(account_type.value))
        if from_account_id:
            self.page.select_option(self.FROM_ACCOUNT_SELECT, from_account_id)
        self.page.click(self.OPEN_ACCOUNT_BTN)
        self.page.wait_for_selector(self.NEW_ACCOUNT_ID, timeout=10000)
        return self.page.locator(self.NEW_ACCOUNT_ID).inner_text()
