"""Root conftest – configures Playwright browser launch options from .env."""

import pytest

from src.config.environment import ENV


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": ENV.headless,
        "slow_mo": ENV.slow_mo,
    }
