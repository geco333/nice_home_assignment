from playwright.sync_api import Page, expect


class BasePage:
    """Base page providing shared navigation and assertion helpers."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "") -> None:
        self.page.goto(f"{self.base_url}/{path}")
        self.page.wait_for_load_state("domcontentloaded")

    def get_title(self) -> str:
        return self.page.title()

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def expect_visible(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_visible()

    def expect_text_contains(self, selector: str, text: str) -> None:
        expect(self.page.locator(selector)).to_contain_text(text)

    def click_link(self, text: str) -> None:
        self.page.get_by_role("link", name=text).click()
        self.page.wait_for_load_state("domcontentloaded")
