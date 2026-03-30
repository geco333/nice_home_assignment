"""Page Object for the ParaBank transfer funds page."""
from src.pages.base_page import BasePage


class TransferFundsPage(BasePage):
    """Encapsulates interactions with the ParaBank fund transfer form."""

    PATH = "transfer.htm"

    AMOUNT_INPUT = "#amount"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    TO_ACCOUNT_SELECT = "#toAccountId"
    TRANSFER_BTN = "input[value='Transfer']"
    SUCCESS_MESSAGE = "#rightPanel h1"
    RESULT_MESSAGE = "#rightPanel p"
    AMOUNT_RESULT = "#amount"
    FROM_ACCOUNT_RESULT = "#fromAccountId"
    TO_ACCOUNT_RESULT = "#toAccountId"
    ERROR_MESSAGE = "#rightPanel p.error"

    def open(self) -> "TransferFundsPage":
        """Navigate to the transfer page and wait for account dropdowns to load.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        self.page.wait_for_selector(self.FROM_ACCOUNT_SELECT, timeout=10000)
        return self

    def transfer(self, amount: str, from_account_id: str, to_account_id: str) -> None:
        """Fill and submit the transfer form.

        :param amount: Dollar amount to transfer (as string).
        :param from_account_id: Source account ID.
        :param to_account_id: Destination account ID.
        """
        self.page.fill(self.AMOUNT_INPUT, amount)
        self.page.select_option(self.FROM_ACCOUNT_SELECT, from_account_id)
        self.page.select_option(self.TO_ACCOUNT_SELECT, to_account_id)
        self.page.click(self.TRANSFER_BTN)
        self.page.wait_for_load_state("domcontentloaded")

    def get_success_heading(self) -> str:
        """Wait for and return the 'Transfer Complete!' heading text."""
        heading = self.page.get_by_text("Transfer Complete!")
        heading.wait_for(timeout=10000)
        return heading.inner_text()

    def is_transfer_complete(self) -> bool:
        """Check whether the 'Transfer Complete!' confirmation is visible."""
        return self.page.get_by_text("Transfer Complete!").is_visible()
