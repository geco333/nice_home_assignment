"""Data models for customer-related domain entities."""
from dataclasses import dataclass


@dataclass
class Address:
    """Postal address associated with a customer."""
    street: str
    city: str
    state: str
    zip_code: str


@dataclass
class CustomerRegistration:
    """All fields needed to register a new ParaBank customer."""
    first_name: str
    last_name: str
    address: Address
    phone_number: str
    ssn: str
    username: str
    password: str


@dataclass
class Customer:
    """Customer record as returned by the ParaBank API."""
    id: int
    first_name: str
    last_name: str
    address: Address
    phone_number: str
    ssn: str


@dataclass
class LoginCredentials:
    """Username/password pair used for authentication."""
    username: str
    password: str
