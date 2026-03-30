"""Dynamic environment configuration backed by ``.env`` files and ``os.environ``."""
import os

from dotenv import load_dotenv

load_dotenv()

_BOOL_FALSY = {"false", "0", "no"}


class EnvironmentConfig:
    """Dynamic config that reads any ``.env`` variable on attribute access.

    Access variables as lowercase attributes::

        ENV.base_url   # reads BASE_URL from env
        ENV.headless   # reads HEADLESS, auto-cast to bool
        ENV.slow_mo    # reads SLOW_MO, auto-cast to int

    Raises :class:`EnvironmentError` if the variable is not set.
    """

    def __getattr__(self, name: str):
        """Look up the upper-cased environment variable and auto-cast its value.

        :param name: Attribute name (converted to upper-case for the env lookup).
        :returns: The auto-cast value (int, float, bool, or str).
        :raises EnvironmentError: If the environment variable is not defined.
        """
        key = name.upper()
        raw = os.environ.get(key)

        if raw is None:
            raise EnvironmentError(f"Required environment variable '{key}' is not set")

        return self._cast(raw)

    @staticmethod
    def _cast(value: str):
        """Auto-cast a raw string to int, float, bool, or leave as str.

        Casting priority: int > float > bool > str.

        :param value: Raw environment variable value.
        :returns: The value in its most specific Python type.
        """
        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        if value.lower() in _BOOL_FALSY | {"true", "yes", "1"}:
            return value.lower() not in _BOOL_FALSY

        return value


ENV = EnvironmentConfig()
