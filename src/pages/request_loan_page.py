"""Page Object for the ParaBank loan request page."""
from src.pages.base_page import BasePage


class RequestLoanPage(BasePage):
    """Encapsulates interactions with the ParaBank loan application form.

    Allows submitting a loan request and reading the approval/denial result.
    """

    PATH = "requestloan.htm"

    # Form fields
    LOAN_AMOUNT = "#amount"
    DOWN_PAYMENT = "#downPayment"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    APPLY_BTN = "input[value='Apply Now']"

    # Result selectors
    RESULT_HEADING = "#requestLoanResult h1"
    LOAN_PROVIDER = "#loanProviderName"
    RESPONSE_DATE = "#responseDate"
    LOAN_STATUS = "#loanStatus"
    NEW_ACCOUNT_ID = "#newAccountId"

    # Approval / denial containers
    APPROVED_CONTAINER = "#loanRequestApproved"
    DENIED_CONTAINER = "#loanRequestDenied"

    # Error
    ERROR_HEADING = "#requestLoanError h1"

    def open(self) -> "RequestLoanPage":
        """Navigate to the loan request page.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        return self

    def apply_for_loan(self, amount: str, down_payment: str, from_account_id: str | None = None) -> None:
        """Fill and submit the loan application form.

        :param amount: Requested loan amount.
        :param down_payment: Down payment amount.
        :param from_account_id: Source account ID; if None, uses the pre-selected account.
        """
        self.page.fill(self.LOAN_AMOUNT, amount)
        self.page.fill(self.DOWN_PAYMENT, down_payment)
        if from_account_id:
            self.page.select_option(self.FROM_ACCOUNT_SELECT, from_account_id)
        self.page.click(self.APPLY_BTN)

    def get_result_heading(self) -> str:
        """Return the heading after the loan is processed (e.g. 'Loan Request Processed')."""
        self.page.wait_for_selector(self.RESULT_HEADING, timeout=10000)
        return self.page.locator(self.RESULT_HEADING).inner_text()

    def get_loan_status(self) -> str:
        """Return the loan approval status text (e.g. 'Approved' or 'Denied')."""
        return self.page.locator(self.LOAN_STATUS).inner_text()

    def get_loan_provider(self) -> str:
        """Return the name of the loan provider."""
        return self.page.locator(self.LOAN_PROVIDER).inner_text()

    def get_new_account_id(self) -> str:
        """Return the new account ID created upon loan approval.

        :returns: Account ID string (only available when loan is approved).
        """
        return self.page.locator(self.NEW_ACCOUNT_ID).inner_text()

    def is_approved(self) -> bool:
        """Check whether the loan approval message is visible."""
        return self.page.locator(self.APPROVED_CONTAINER).is_visible()

    def is_denied(self) -> bool:
        """Check whether the loan denial message is visible."""
        return self.page.locator(self.DENIED_CONTAINER).is_visible()
