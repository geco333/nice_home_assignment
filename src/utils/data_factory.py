import random
import string

from src.models.customer import Address, CustomerRegistration, LoginCredentials


def _random_id(length: int = 6) -> str:
    """
    Will return a random ID containing lowercase letters and digits.
    
    :param length: The length of the generated ID.

    :return: A random ID string.
    """
    
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _random_digits(length: int) -> str:
    """
    Returns a random string of digits.
    
    :param length: The length of the generated ID.

    :return: Random string of digits.
    """
    
    return "".join(random.choices(string.digits, k=length))


def create_customer_registration(**overrides) -> CustomerRegistration:
    """
    Return a CustomerRegistration object, by default all properties are random,
    can override any property by passing as keyword arguments.
    
    :param overrides: Set property by passing it as a keyword argument.

    :return: A CustomerRegistration object.
    """
    
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
    """
    Return a LoginCredentials object from a CustomerRegistration object.
    
    :param registration: The CustomerRegistration object to use.

    :return: LoginCredentials object.
    """
    
    return LoginCredentials(username=registration.username, password=registration.password)


def random_transfer_amount(min_val: int = 10, max_val: int = 100) -> int:
    """"Return a random transfer amount between min_val and max_val.
    
    :param min_val: Minimum random range.
    :param max_val: Maximum random range.

    :return: An int between min_val and max_val.
    """
    
    return random.randint(min_val, max_val)
