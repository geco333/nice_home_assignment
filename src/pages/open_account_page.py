from src.models.account import AccountType
from src.pages.base_page import BasePage


class OpenAccountPage(BasePage):

    PATH = "openaccount.htm"

    ACCOUNT_TYPE_SELECT = "#type"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    OPEN_ACCOUNT_BTN = "input[value='Open New Account']"
    NEW_ACCOUNT_ID = "#newAccountId"
    SUCCESS_MESSAGE = "#rightPanel h1"

    def open(self) -> "OpenAccountPage":
        self.navigate(self.PATH)
        self.page.wait_for_selector(self.FROM_ACCOUNT_SELECT, timeout=10000)
        return self

    def create_account(self, account_type: AccountType, from_account_id: str | None = None) -> str:
        self.page.select_option(self.ACCOUNT_TYPE_SELECT, str(account_type.value))
        if from_account_id:
            self.page.select_option(self.FROM_ACCOUNT_SELECT, from_account_id)
        self.page.click(self.OPEN_ACCOUNT_BTN)
        self.page.wait_for_selector(self.NEW_ACCOUNT_ID, timeout=10000)
        return self.page.locator(self.NEW_ACCOUNT_ID).inner_text()
