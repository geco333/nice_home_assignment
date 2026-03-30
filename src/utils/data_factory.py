import random
import string

from src.models.customer import Address, CustomerRegistration, LoginCredentials


def _random_id(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _random_digits(length: int) -> str:
    return "".join(random.choices(string.digits, k=length))


def create_customer_registration(**overrides) -> CustomerRegistration:
    uid = _random_id()
    defaults = dict(
        first_name=f"Test_{uid}",
        last_name=f"User{uid}",
        address=Address(
            street=f"{_random_digits(3)} Automation St",
            city=f"TestCity_{uid}",
            state=f"CA_{uid}",
            zip_code=str(_random_digits(5)),
        ),
        phone_number=f"555{_random_digits(7)}",
        ssn=f"{_random_digits(3)}-{_random_digits(2)}-{_random_digits(4)}",
        username=f"testuser_{uid}",
        password=f"Pass{uid}!23",
    )
    defaults.update(overrides)
    
    return CustomerRegistration(**defaults)


def credentials_from(registration: CustomerRegistration) -> LoginCredentials:
    return LoginCredentials(username=registration.username, password=registration.password)


def random_transfer_amount(min_val: int = 10, max_val: int = 100) -> int:
    return random.randint(min_val, max_val)
