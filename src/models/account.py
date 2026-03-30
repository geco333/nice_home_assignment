"""Data models for account and transaction domain entities."""
from dataclasses import dataclass
from enum import IntEnum


class AccountType(IntEnum):
    """ParaBank account type codes used in API requests."""
    CHECKING = 0
    SAVINGS = 1


@dataclass
class Account:
    """Bank account record as returned by the ParaBank API."""
    id: int
    customer_id: int
    type: str
    balance: float


@dataclass
class Transaction:
    """Single transaction record associated with an account."""
    id: int
    account_id: int
    type: str
    date: str
    amount: float
    description: str
