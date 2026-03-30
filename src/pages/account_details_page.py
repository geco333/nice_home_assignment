"""Page Object for the ParaBank account details / activity page."""
from src.pages.base_page import BasePage
from src.utils.helpers import parse_balance


class AccountDetailsPage(BasePage):
    """Encapsulates interactions with the ParaBank account details and activity page.

    Displays account metadata (number, type, balance) and a filterable
    transaction history table.
    """

    # Account details
    ACCOUNT_ID = "#accountId"
    ACCOUNT_TYPE = "#accountType"
    BALANCE = "#balance"
    AVAILABLE_BALANCE = "#availableBalance"

    # Activity filter
    MONTH_SELECT = "#month"
    TRANSACTION_TYPE_SELECT = "#transactionType"
    GO_BTN = "input[value='Go']"

    # Transaction table
    TRANSACTION_TABLE = "#transactionTable"
    TRANSACTION_ROWS = "#transactionTable tbody tr"
    NO_TRANSACTIONS = "#noTransactions"

    # Error
    ERROR_CONTAINER = "#error"

    def get_account_id(self) -> str:
        """Return the account number displayed on the page."""
        return self.page.locator(self.ACCOUNT_ID).inner_text()

    def get_account_type(self) -> str:
        """Return the account type (e.g. 'CHECKING' or 'SAVINGS')."""
        return self.page.locator(self.ACCOUNT_TYPE).inner_text()

    def get_balance(self) -> float:
        """Return the current account balance as a float.

        :returns: Numeric balance parsed from the displayed currency string.
        """
        return parse_balance(self.page.locator(self.BALANCE).inner_text())

    def get_available_balance(self) -> float:
        """Return the available balance as a float.

        :returns: Numeric available balance parsed from the displayed currency string.
        """
        return parse_balance(self.page.locator(self.AVAILABLE_BALANCE).inner_text())

    def filter_activity(self, month: str | None = None, transaction_type: str | None = None) -> None:
        """Apply activity filters and submit.

        :param month: Activity period (e.g. 'All', 'January', 'March').
        :param transaction_type: Transaction type filter (e.g. 'All', 'Credit', 'Debit').
        """
        if month:
            self.page.select_option(self.MONTH_SELECT, month)
        if transaction_type:
            self.page.select_option(self.TRANSACTION_TYPE_SELECT, transaction_type)
        self.page.click(self.GO_BTN)

    def get_transaction_count(self) -> int:
        """Return the number of transaction rows displayed.

        :returns: Count of visible transaction rows, or 0 if the table is hidden.
        """
        if not self.page.locator(self.TRANSACTION_TABLE).is_visible():
            return 0
        return self.page.locator(self.TRANSACTION_ROWS).count()

    def has_no_transactions(self) -> bool:
        """Check whether the 'No transactions found' message is visible."""
        return self.page.locator(self.NO_TRANSACTIONS).is_visible()

    def is_error_visible(self) -> bool:
        """Check whether the error container is displayed."""
        return self.page.locator(self.ERROR_CONTAINER).is_visible()
