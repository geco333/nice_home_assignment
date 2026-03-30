"""Page Object for the ParaBank customer care (contact) page."""
from src.pages.base_page import BasePage


class ContactPage(BasePage):
    """Encapsulates interactions with the ParaBank contact / customer care form.

    Allows submitting a support request with name, email, phone, and message.
    """

    PATH = "contact.htm"

    # Form fields
    NAME = "#name"
    EMAIL = "#email"
    PHONE = "#phone"
    MESSAGE = "#message"
    SEND_BTN = "input[value='Send to Customer Care']"

    # Result
    SUCCESS_HEADING = "#rightPanel h1"
    SUCCESS_MESSAGE = "#rightPanel p"

    # Validation errors
    ERROR_MESSAGES = "span.error"

    def open(self) -> "ContactPage":
        """Navigate to the contact page.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        return self

    def send_message(self, name: str, email: str, phone: str, message: str) -> None:
        """Fill and submit the customer care form.

        :param name: Sender's full name.
        :param email: Sender's email address.
        :param phone: Sender's phone number.
        :param message: Message body.
        """
        self.page.fill(self.NAME, name)
        self.page.fill(self.EMAIL, email)
        self.page.fill(self.PHONE, phone)
        self.page.fill(self.MESSAGE, message)

        self.page.click(self.SEND_BTN)
        self.page.wait_for_load_state("domcontentloaded")

    def get_success_heading(self) -> str:
        """Return the heading shown after successful submission (e.g. 'Customer Care')."""
        return self.page.locator(self.SUCCESS_HEADING).inner_text()

    def get_success_message(self) -> str:
        """Return the confirmation message after submission."""
        return self.page.locator(self.SUCCESS_MESSAGE).inner_text()

    def get_error_messages(self) -> list[str]:
        """Return all validation error messages displayed on the form.

        :returns: List of error strings; empty if no errors are shown.
        """
        return self.page.locator(self.ERROR_MESSAGES).all_inner_texts()
