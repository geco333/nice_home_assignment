from src.pages.base_page import BasePage


class TransferFundsPage(BasePage):

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
        self.navigate(self.PATH)
        self.page.wait_for_selector(self.FROM_ACCOUNT_SELECT, timeout=10000)
        return self

    def transfer(self, amount: str, from_account_id: str, to_account_id: str) -> None:
        self.page.fill(self.AMOUNT_INPUT, amount)
        self.page.select_option(self.FROM_ACCOUNT_SELECT, from_account_id)
        self.page.select_option(self.TO_ACCOUNT_SELECT, to_account_id)
        self.page.click(self.TRANSFER_BTN)
        self.page.wait_for_load_state("domcontentloaded")

    def get_success_heading(self) -> str:
        heading = self.page.get_by_text("Transfer Complete!")
        heading.wait_for(timeout=10000)
        return heading.inner_text()

    def is_transfer_complete(self) -> bool:
        return self.page.get_by_text("Transfer Complete!").is_visible()
