import functools
import logging
import time

from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger("parabank.retry")


def retry_on_failure(retries: int = 3, delay: float = 1.0):
    """Decorator that retries a function on Playwright TimeoutError.

    Args:
        retries: Total number of attempts before giving up.
        delay: Seconds to wait between retries.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except PlaywrightTimeoutError as exc:
                    last_error = exc

                    if attempt < retries:
                        logger.warning(
                            "⚠️ Attempt %d/%d failed for %s: %s — retrying in %.1fs",
                            attempt, retries, func.__qualname__, exc, delay,
                        )
                        time.sleep(delay)

            raise last_error

        return wrapper

    return decorator
