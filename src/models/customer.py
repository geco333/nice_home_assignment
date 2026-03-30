from dataclasses import dataclass


@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str


@dataclass
class CustomerRegistration:
    first_name: str
    last_name: str
    address: Address
    phone_number: str
    ssn: str
    username: str
    password: str


@dataclass
class Customer:
    id: int
    first_name: str
    last_name: str
    address: Address
    phone_number: str
    ssn: str


@dataclass
class LoginCredentials:
    username: str
    password: str
