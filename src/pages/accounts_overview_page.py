"""Page Object for the ParaBank accounts overview page."""
from playwright.sync_api import expect

from src.pages.base_page import BasePage
from src.utils.helpers import parse_balance


class AccountsOverviewPage(BasePage):
    """Encapsulates interactions with the ParaBank accounts overview table."""

    PATH = "overview.htm"

    ACCOUNTS_TABLE = "#accountTable"
    ACCOUNT_LINKS = "#accountTable a"
    TOTAL_BALANCE = "#accountTable tfoot td:nth-child(2)"

    def open(self) -> "AccountsOverviewPage":
        """Navigate to the accounts overview page.

        :returns: Self for method chaining.
        """
        self.navigate(self.PATH)
        return self

    def get_account_ids(self) -> list[str]:
        """Return all account IDs listed in the overview table.

        :returns: List of account ID strings.
        """
        self.page.wait_for_selector(self.ACCOUNT_LINKS, timeout=10000)
        return self.page.locator(self.ACCOUNT_LINKS).all_inner_texts()

    def account_exists(self, account_id: str) -> bool:
        """Check whether the given account ID appears in the overview table.

        :param account_id: Account ID to look for.
        :returns: True if the account is listed.
        """
        return account_id in self.get_account_ids()

    def get_account_balance(self, account_id: str) -> float:
        """Return the displayed balance for a specific account.

        :param account_id: Account ID whose balance to read.
        :returns: Balance as a float.
        """
        row = self.page.locator(f"{self.ACCOUNTS_TABLE} tr:has(a:text-is('{account_id}'))")
        balance_cell = row.locator("td:nth-child(2)")
        expect(balance_cell).to_be_visible()
        return parse_balance(balance_cell.inner_text())

    def click_account(self, account_id: str) -> None:
        """Click on an account link to navigate to its detail page.

        :param account_id: Account ID link to click.
        """
        self.page.locator(f"{self.ACCOUNTS_TABLE} a:text-is('{account_id}')").click()
        self.page.wait_for_load_state("domcontentloaded")

    def get_total_balance(self) -> float:
        """Return the total balance shown in the table footer.

        :returns: Total balance as a float.
        """
        return parse_balance(self.page.locator(self.TOTAL_BALANCE).inner_text())
