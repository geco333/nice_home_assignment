from src.models.customer import LoginCredentials
from src.pages.base_page import BasePage


class LoginPage(BasePage):

    PATH = "index.htm"

    USERNAME = "input[name='username']"
    PASSWORD = "input[name='password']"
    LOGIN_BTN = "input[value='Log In']"
    ERROR_MESSAGE = "#rightPanel p.error"
    WELCOME_MESSAGE = "#rightPanel h1.title:first-of-type"

    def open(self) -> "LoginPage":
        self.navigate(self.PATH)
        return self

    def login(self, credentials: LoginCredentials) -> None:
        self.page.fill(self.USERNAME, credentials.username)
        self.page.fill(self.PASSWORD, credentials.password)
        self.page.click(self.LOGIN_BTN)
        self.page.wait_for_load_state("domcontentloaded")

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def get_welcome_message(self) -> str:
        return self.page.locator("#rightPanel h1").first.inner_text()

    def is_logged_in(self) -> bool:
        return self.page.locator(self.WELCOME_MESSAGE).is_visible()
