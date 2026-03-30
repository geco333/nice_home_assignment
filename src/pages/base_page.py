"""Base Page Object providing shared navigation and automatic retry for all subclasses."""
import inspect

from playwright.sync_api import Page

from src.config.environment import ENV
from src.utils.retry import retry_on_failure


class BasePage:
    """Base page providing shared navigation helpers.

    All public methods defined in subclasses are automatically wrapped
    with a retry-on-failure decorator via ``__init_subclass__``.
    Retry count and delay are read from environment variables
    ``RETRY_COUNT`` and ``RETRY_DELAY``.
    """

    RETRY_COUNT = ENV.retry_count
    RETRY_DELAY = ENV.retry_delay

    def __init_subclass__(cls, **kwargs):
        """Wrap every public method of each POM subclass with retry logic."""
        super().__init_subclass__(**kwargs)

        for name, method in list(vars(cls).items()):
            if not name.startswith("_") and inspect.isfunction(method):
                setattr(cls, name, retry_on_failure(cls.RETRY_COUNT, cls.RETRY_DELAY)(method))

    def __init__(self, page: Page, base_url: str):
        """Initialize with a Playwright Page and the application base URL.

        :param page: Playwright Page instance to drive.
        :param base_url: Root URL of the web application (e.g. ``https://parabank.parasoft.com/parabank``).
        """
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "") -> None:
        """Navigate to a path relative to the base URL and wait for DOM content to load.

        :param path: Relative path to append to the base URL.
        """
        self.page.goto(f"{self.base_url}/{path}")
        self.page.wait_for_load_state("domcontentloaded")

    def get_title(self) -> str:
        """Return the current page title."""
        return self.page.title()
