from playwright.sync_api import expect

from src.pages.base_page import BasePage
from src.utils.helpers import parse_balance


class AccountsOverviewPage(BasePage):

    PATH = "overview.htm"

    ACCOUNTS_TABLE = "#accountTable"
    ACCOUNT_LINKS = "#accountTable a"
    TOTAL_BALANCE = "#accountTable tfoot td:nth-child(2)"

    def open(self) -> "AccountsOverviewPage":
        self.navigate(self.PATH)
        return self

    def get_account_ids(self) -> list[str]:
        self.page.wait_for_selector(self.ACCOUNT_LINKS, timeout=10000)
        return self.page.locator(self.ACCOUNT_LINKS).all_inner_texts()

    def account_exists(self, account_id: str) -> bool:
        return account_id in self.get_account_ids()

    def get_account_balance(self, account_id: str) -> float:
        row = self.page.locator(f"{self.ACCOUNTS_TABLE} tr:has(a:text-is('{account_id}'))")
        balance_cell = row.locator("td:nth-child(2)")
        expect(balance_cell).to_be_visible()
        return parse_balance(balance_cell.inner_text())

    def click_account(self, account_id: str) -> None:
        self.page.locator(f"{self.ACCOUNTS_TABLE} a:text-is('{account_id}')").click()
        self.page.wait_for_load_state("domcontentloaded")

    def get_total_balance(self) -> float:
        return parse_balance(self.page.locator(self.TOTAL_BALANCE).inner_text())
