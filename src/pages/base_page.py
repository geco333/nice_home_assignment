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
        super().__init_subclass__(**kwargs)

        for name, method in list(vars(cls).items()):
            if not name.startswith("_") and inspect.isfunction(method):
                setattr(cls, name, retry_on_failure(cls.RETRY_COUNT, cls.RETRY_DELAY)(method))

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "") -> None:
        self.page.goto(f"{self.base_url}/{path}")
        self.page.wait_for_load_state("domcontentloaded")

    def get_title(self) -> str:
        return self.page.title()
