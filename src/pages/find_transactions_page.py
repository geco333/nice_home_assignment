"""Page Object for the ParaBank find-transactions page."""
from src.pages.base_page import BasePage


class FindTransactionsPage(BasePage):
    """Encapsulates interactions with the ParaBank transaction search form.

    Supports searching by transaction ID, date, date range, and amount.
    """

    PATH = "findtrans.htm"

    # Form controls
    ACCOUNT_SELECT = "#accountId"
    TRANSACTION_ID_INPUT = "#transactionId"
    TRANSACTION_DATE_INPUT = "#transactionDate"
    FROM_DATE_INPUT = "#fromDate"
    TO_DATE_INPUT = "#toDate"
    AMOUNT_INPUT = "#amount"

    # Submit buttons
    FIND_BY_ID_BTN = "#findById"
    FIND_BY_DATE_BTN = "#findByDate"
    FIND_BY_DATE_RANGE_BTN = "#findByDateRange"
    FIND_BY_AMOUNT_BTN = "#findByAmount"

    # Results
    RESULT_HEADING = "#resultContainer h1"
    TRANSACTION_TABLE = "#transactionTable"
    TRANSACTION_ROWS = "#transactionBody tr"
    NO_RESULTS_MESSAGE = "#resultContainer p"

    # Errors
    ACCOUNT_ID_ERROR = "#accountIdError"
    TRANSACTION_ID_ERROR = "#transactionIdError"
    TRANSACTION_DATE_ERROR = "#transactionDateError"
    DATE_RANGE_ERROR = "#dateRangeError"
    AMOUNT_ERROR = "#amountError"
    ERROR_HEADING = "#errorContainer h1"

    def open(self) -> "FindTransactionsPage":
        """Navigate to the find-transactions page.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        return self

    def select_account(self, account_id: str) -> None:
        """Select an account from the dropdown.

        :param account_id: Account ID to select.
        """
        self.page.select_option(self.ACCOUNT_SELECT, account_id)

    def find_by_id(self, transaction_id: str) -> None:
        """Search for a transaction by its ID.

        :param transaction_id: Transaction ID to look up.
        """
        self.page.fill(self.TRANSACTION_ID_INPUT, transaction_id)
        self.page.click(self.FIND_BY_ID_BTN)

    def find_by_date(self, date: str) -> None:
        """Search for transactions on a specific date.

        :param date: Date string in MM-DD-YYYY format.
        """
        self.page.fill(self.TRANSACTION_DATE_INPUT, date)
        self.page.click(self.FIND_BY_DATE_BTN)

    def find_by_date_range(self, from_date: str, to_date: str) -> None:
        """Search for transactions within a date range.

        :param from_date: Start date in MM-DD-YYYY format.
        :param to_date: End date in MM-DD-YYYY format.
        """
        self.page.fill(self.FROM_DATE_INPUT, from_date)
        self.page.fill(self.TO_DATE_INPUT, to_date)
        self.page.click(self.FIND_BY_DATE_RANGE_BTN)

    def find_by_amount(self, amount: str) -> None:
        """Search for transactions by amount.

        :param amount: Dollar amount to search for.
        """
        self.page.fill(self.AMOUNT_INPUT, amount)
        self.page.click(self.FIND_BY_AMOUNT_BTN)

    def get_result_heading(self) -> str:
        """Return the result heading text (e.g. 'Transaction Results')."""
        self.page.wait_for_selector(self.RESULT_HEADING, timeout=10000)
        return self.page.locator(self.RESULT_HEADING).inner_text()

    def get_transaction_count(self) -> int:
        """Return the number of transaction rows in the results table.

        :returns: Count of visible transaction rows.
        """
        self.page.wait_for_selector(self.TRANSACTION_ROWS, timeout=10000)
        return self.page.locator(self.TRANSACTION_ROWS).count()

    def is_results_visible(self) -> bool:
        """Check whether the results container is displayed."""
        return self.page.locator("#resultContainer").is_visible()

    def is_error_visible(self) -> bool:
        """Check whether the error container is displayed."""
        return self.page.locator("#errorContainer").is_visible()
