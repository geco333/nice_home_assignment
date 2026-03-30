from src.models.customer import CustomerRegistration
from src.pages.base_page import BasePage


class RegisterPage(BasePage):

    PATH = "register.htm"

    FIRST_NAME = "#customer\\.firstName"
    LAST_NAME = "#customer\\.lastName"
    ADDRESS = "#customer\\.address\\.street"
    CITY = "#customer\\.address\\.city"
    STATE = "#customer\\.address\\.state"
    ZIP_CODE = "#customer\\.address\\.zipCode"
    PHONE = "#customer\\.phoneNumber"
    SSN = "#customer\\.ssn"
    USERNAME = "#customer\\.username"
    PASSWORD = "#customer\\.password"
    CONFIRM_PASSWORD = "#repeatedPassword"
    REGISTER_BTN = "input[value='Register']"

    SUCCESS_HEADING = "#rightPanel h1"
    SUCCESS_MESSAGE = "#rightPanel p"
    ERROR_MESSAGES = "span.error"

    def open(self) -> "RegisterPage":
        self.navigate(self.PATH)
        return self

    def register(self, customer: CustomerRegistration) -> None:
        self.page.fill(self.FIRST_NAME, customer.first_name)
        self.page.fill(self.LAST_NAME, customer.last_name)
        self.page.fill(self.ADDRESS, customer.address.street)
        self.page.fill(self.CITY, customer.address.city)
        self.page.fill(self.STATE, customer.address.state)
        self.page.fill(self.ZIP_CODE, customer.address.zip_code)
        self.page.fill(self.PHONE, customer.phone_number)
        self.page.fill(self.SSN, customer.ssn)
        self.page.fill(self.USERNAME, customer.username)
        self.page.fill(self.PASSWORD, customer.password)
        self.page.fill(self.CONFIRM_PASSWORD, customer.password)

        self.page.click(self.REGISTER_BTN)
        self.page.wait_for_load_state("domcontentloaded")

    def get_success_heading(self) -> str:
        return self.page.locator(self.SUCCESS_HEADING).inner_text()

    def get_success_message(self) -> str:
        return self.page.locator(self.SUCCESS_MESSAGE).inner_text()

    def get_error_messages(self) -> list[str]:
        return self.page.locator(self.ERROR_MESSAGES).all_inner_texts()
