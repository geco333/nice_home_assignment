"""Page Object for the ParaBank bill payment page."""
from src.pages.base_page import BasePage


class BillPayPage(BasePage):
    """Encapsulates interactions with the ParaBank bill payment form.

    Allows filling payee details, specifying an amount and source account,
    submitting the payment, and reading the confirmation or validation errors.
    """

    PATH = "billpay.htm"

    # Payee information
    PAYEE_NAME = "input[name='payee.name']"
    PAYEE_ADDRESS = "input[name='payee.address.street']"
    PAYEE_CITY = "input[name='payee.address.city']"
    PAYEE_STATE = "input[name='payee.address.state']"
    PAYEE_ZIP_CODE = "input[name='payee.address.zipCode']"
    PAYEE_PHONE = "input[name='payee.phoneNumber']"
    PAYEE_ACCOUNT = "input[name='payee.accountNumber']"
    VERIFY_ACCOUNT = "input[name='verifyAccount']"

    # Payment details
    AMOUNT = "input[name='amount']"
    FROM_ACCOUNT_SELECT = "select[name='fromAccountId']"
    SEND_PAYMENT_BTN = "input[value='Send Payment']"

    # Result selectors
    RESULT_PAYEE_NAME = "#payeeName"
    RESULT_AMOUNT = "#amount"
    RESULT_FROM_ACCOUNT = "#fromAccountId"
    SUCCESS_HEADING = "#billpayResult h1"

    # Validation errors
    ERROR_NAME = "#validationModel-name"
    ERROR_ADDRESS = "#validationModel-address"
    ERROR_CITY = "#validationModel-city"
    ERROR_STATE = "#validationModel-state"
    ERROR_ZIP_CODE = "#validationModel-zipCode"
    ERROR_PHONE = "#validationModel-phoneNumber"
    ERROR_ACCOUNT_EMPTY = "#validationModel-account-empty"
    ERROR_ACCOUNT_INVALID = "#validationModel-account-invalid"
    ERROR_VERIFY_EMPTY = "#validationModel-verifyAccount-empty"
    ERROR_VERIFY_MISMATCH = "#validationModel-verifyAccount-mismatch"
    ERROR_AMOUNT_EMPTY = "#validationModel-amount-empty"
    ERROR_AMOUNT_INVALID = "#validationModel-amount-invalid"

    def open(self) -> "BillPayPage":
        """Navigate to the bill pay page.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        return self

    def fill_payee_info(
        self,
        name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        phone: str,
        account_number: str,
    ) -> None:
        """Fill all payee information fields.

        :param name: Payee name.
        :param address: Payee street address.
        :param city: Payee city.
        :param state: Payee state.
        :param zip_code: Payee zip code.
        :param phone: Payee phone number.
        :param account_number: Payee account number (filled in both account and verify fields).
        """
        self.page.fill(self.PAYEE_NAME, name)
        self.page.fill(self.PAYEE_ADDRESS, address)
        self.page.fill(self.PAYEE_CITY, city)
        self.page.fill(self.PAYEE_STATE, state)
        self.page.fill(self.PAYEE_ZIP_CODE, zip_code)
        self.page.fill(self.PAYEE_PHONE, phone)
        self.page.fill(self.PAYEE_ACCOUNT, account_number)
        self.page.fill(self.VERIFY_ACCOUNT, account_number)

    def send_payment(self, amount: str, from_account_id: str | None = None) -> None:
        """Fill the amount, optionally select the source account, and submit the payment.

        :param amount: Dollar amount to pay.
        :param from_account_id: Source account ID; if None, uses the pre-selected account.
        """
        self.page.fill(self.AMOUNT, amount)

        if from_account_id:
            self.page.select_option(self.FROM_ACCOUNT_SELECT, from_account_id)

        self.page.click(self.SEND_PAYMENT_BTN)

    def get_success_heading(self) -> str:
        """Return the heading text after a successful payment (e.g. 'Bill Payment Complete')."""
        self.page.wait_for_selector(self.SUCCESS_HEADING, timeout=10000)

        return self.page.locator(self.SUCCESS_HEADING).inner_text()

    def get_result_payee_name(self) -> str:
        """Return the payee name shown in the payment confirmation."""
        return self.page.locator(self.RESULT_PAYEE_NAME).inner_text()

    def get_result_amount(self) -> str:
        """Return the formatted amount shown in the payment confirmation."""
        return self.page.locator(self.RESULT_AMOUNT).inner_text()

    def get_visible_errors(self) -> list[str]:
        """Return the text of all currently visible validation error messages.

        :returns: List of visible error message strings.
        """
        errors = self.page.locator("span.error:visible")
        
        return errors.all_inner_texts()
