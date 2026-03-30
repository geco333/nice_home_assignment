from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class EnvironmentConfig:
    base_url: str
    api_base_url: str
    headless: bool
    slow_mo: int
    timeout: int


def _bool_env(key: str, default: bool) -> bool:
    return os.getenv(key, str(default)).lower() not in ("false", "0", "no")


ENV = EnvironmentConfig(
    base_url=os.getenv("BASE_URL", "https://parabank.parasoft.com/parabank"),
    api_base_url=os.getenv("API_BASE_URL", "https://parabank.parasoft.com/parabank/services/bank"),
    headless=_bool_env("HEADLESS", True),
    slow_mo=int(os.getenv("SLOW_MO", "0")),
    timeout=int(os.getenv("TIMEOUT", "30000")),
)
