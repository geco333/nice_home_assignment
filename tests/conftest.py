"""Shared fixtures, hooks, and logging setup for all test modules.

Provides:
- Allure results directory configuration
- Timestamped per-run log files with per-test slicing attached to Allure
- Screenshot capture on test failure
- Session-scoped API client fixtures
- Class-scoped ``shared_page`` and ``shared_context`` fixtures for E2E workflows
"""
import dataclasses
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterator

import allure
import pytest
from playwright.sync_api import Page

from src.api.account_api import AccountApi
from src.api.api_client import ApiClient
from src.api.customer_api import CustomerApi
from src.config.environment import ENV


def pytest_configure(config):
    """Set the Allure results directory from ``.env`` if not provided via CLI.

    Conftest ``pytest_configure`` hooks run before installed-plugin hooks
    (pluggy LIFO order), so setting ``allure_report_dir`` here ensures the
    ``allure-pytest`` plugin sees it when its own ``pytest_configure`` runs
    immediately after.
    """
    if not config.option.allure_report_dir:
        results_dir = Path(ENV.allure_results_dir)
        results_dir.mkdir(parents=True, exist_ok=True)
        config.option.allure_report_dir = str(results_dir)


# ── Logging setup ────────────────────────────────────────────

_log_file_path: Path | None = None
_log_read_offset: int = 0


def _setup_logging() -> logging.Logger:
    """Create a timestamped log file and configure the ``parabank`` logger hierarchy.

    :returns: The root ``parabank`` logger instance.
    """
    global _log_file_path

    log_dir = Path(ENV.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    _log_file_path = log_dir / f"test_run_{timestamp}.log"

    _logger = logging.getLogger("parabank")
    _logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(_log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s][%(name)s][%(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    _logger.addHandler(file_handler)
    _logger.propagate = False
    _logger.info("Log file: %s", _log_file_path)

    return _logger


logger = _setup_logging()


def pytest_runtest_logstart(nodeid):
    """Log a banner when a test starts running."""
    logger.info("───────────────────────── STARTED  %s ─────────────────────────", nodeid)


def pytest_runtest_logfinish(nodeid):
    """Log a banner when a test finishes running."""
    logger.info("───────────────────────── FINISHED %s ─────────────────────────", nodeid)


def _flush_and_read_new_log_lines() -> str:
    """Flush the file handler and return log content written since the last read.

    Tracks a global offset so each call returns only *new* lines,
    enabling per-test log slicing in the Allure report.

    :returns: Log text since the previous call (or empty string).
    """
    global _log_read_offset

    if not _log_file_path or not _log_file_path.exists():
        return ""

    for handler in logger.handlers:
        handler.flush()

    with open(_log_file_path, encoding="utf-8") as f:
        f.seek(_log_read_offset)
        content = f.read()
        _log_read_offset = f.tell()

    return content


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Log test outcomes, attach per-test log slice + shared_context, and capture a screenshot on failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if report.passed:
        logger.info("PASSED   %s", item.nodeid)
    elif report.skipped:
        logger.warning("SKIPPED  %s", item.nodeid)
    else:
        logger.error("FAILED   %s", item.nodeid)

    log_slice = _flush_and_read_new_log_lines()

    if log_slice and _log_file_path:
        allure.attach(
            log_slice,
            name=_log_file_path.name,
            attachment_type=allure.attachment_type.TEXT,
        )

    shared_ctx = item.funcargs.get("shared_context")
    
    if shared_ctx:
        def _serialize(obj):
            """JSON serializer that converts dataclass instances to dicts."""
            if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
                return dataclasses.asdict(obj)
            return str(obj)

        allure.attach(
            json.dumps(shared_ctx, indent=2, default=_serialize),
            name="shared_context",
            attachment_type=allure.attachment_type.JSON,
        )

    if not report.failed:
        return

    page = item.funcargs.get("shared_page") or item.funcargs.get("page")
    
    if page is None:
        return

    screenshot_dir = Path(ENV.screenshot_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    test_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
    path = screenshot_dir / f"{test_name}.png"

    try:
        page.screenshot(path=str(path), full_page=True)
        allure.attach.file(str(path), name=test_name, attachment_type=allure.attachment_type.PNG)
        logger.info("Screenshot saved: %s", path)
    except Exception as exc:
        logger.warning("Screenshot failed: %s", exc)


# ── Playwright browser configuration ─────────────────────────

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Override default browser context args: maximized viewport and HTTPS error tolerance.

    Headed mode: ``viewport=None`` + ``--start-maximized`` fills the screen.
    Headless mode: uses a 1920x1080 viewport since there is no physical screen.
    """
    viewport = None if not ENV.headless else {"width": 1920, "height": 1080}
    return {
        **browser_context_args,
        "viewport": viewport,
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Override default browser launch args with headless/slow_mo from environment."""
    args = list(browser_type_launch_args.get("args", []))
    if not ENV.headless:
        args.append("--start-maximized")
    return {
        **browser_type_launch_args,
        "headless": ENV.headless,
        "slow_mo": ENV.slow_mo,
        "args": args,
    }


# ── API fixtures ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def api_client():
    """Session-scoped :class:`ApiClient` reused across all tests."""
    client = ApiClient(ENV.api_base_url)
    
    yield client
    
    client.close()


@pytest.fixture(scope="session")
def customer_api(api_client: ApiClient) -> CustomerApi:
    """Session-scoped :class:`CustomerApi` backed by the shared API client."""
    return CustomerApi(api_client)


@pytest.fixture(scope="session")
def account_api(api_client: ApiClient) -> AccountApi:
    """Session-scoped :class:`AccountApi` backed by the shared API client."""
    return AccountApi(api_client)


# ── E2E workflow fixtures ─────────────────────────────────────

@pytest.fixture(scope="class")
def shared_page(browser) -> Iterator[Page]:
    """Class-scoped Playwright Page so the browser session persists across ordered test methods."""
    viewport = None if not ENV.headless else {"width": 1920, "height": 1080}
    context = browser.new_context(
        viewport=viewport,
        ignore_https_errors=True,
    )
    page = context.new_page()

    yield page

    context.close()


@pytest.fixture(scope="class")
def shared_context() -> dict:
    """Mutable dict shared across all tests within a class for passing workflow data."""
    return {}
