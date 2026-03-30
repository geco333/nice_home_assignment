from dataclasses import dataclass
from enum import IntEnum


class AccountType(IntEnum):
    CHECKING = 0
    SAVINGS = 1


@dataclass
class Account:
    id: int
    customer_id: int
    type: str
    balance: float


@dataclass
class Transaction:
    id: int
    account_id: int
    type: str
    date: str
    amount: float
    description: str
