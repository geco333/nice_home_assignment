"""Customer-related API operations (registration, login, lookup)."""
from src.api.api_client import ApiClient
from src.models.customer import Customer, Address, CustomerRegistration


class CustomerApi:
    """Operations against the ``/customers`` and ``/login`` endpoints."""

    def __init__(self, client: ApiClient):
        """Initialize with an existing :class:`ApiClient` instance.

        :param client: Configured API client.
        """
        self.client = client

    def register(self, customer: CustomerRegistration, base_url: str) -> None:
        """Register a new customer via HTTP POST to the registration form.

        Uses a separate ``requests.Session`` to first ``GET`` the registration
        page (establishing server-side session cookies) and then ``POST``
        the form data.

        :param customer: Registration data for the new user.
        :param base_url: Application base URL (e.g. ``https://parabank.parasoft.com/parabank``).
        :raises AssertionError: If the response body does not contain the expected success text.
        """
        import requests as _requests

        session = _requests.Session()
        session.verify = False

        session.get(f"{base_url}/register.htm", timeout=self.client.timeout)

        response = session.post(
            f"{base_url}/register.htm",
            data={
                "customer.firstName": customer.first_name,
                "customer.lastName": customer.last_name,
                "customer.address.street": customer.address.street,
                "customer.address.city": customer.address.city,
                "customer.address.state": customer.address.state,
                "customer.address.zipCode": customer.address.zip_code,
                "customer.phoneNumber": customer.phone_number,
                "customer.ssn": customer.ssn,
                "customer.username": customer.username,
                "customer.password": customer.password,
                "repeatedPassword": customer.password,
            },
            timeout=self.client.timeout,
        )
        response.raise_for_status()
        body = response.text.lower()
        assert "welcome" in body or "created successfully" in body, (
            f"Registration failed — unexpected response (status {response.status_code})"
        )

    def login(self, username: str, password: str) -> dict:
        """Login via API and return the customer JSON payload.

        :param username: Customer username.
        :param password: Customer password.
        :returns: Parsed JSON dict from the login response.
        """
        response = self.client.get(f"login/{username}/{password}")
        response.raise_for_status()

        return response.json()

    def get_customer(self, customer_id: int) -> Customer:
        """Retrieve full customer details by ID.

        :param customer_id: Numeric customer identifier.
        :returns: Populated :class:`Customer` dataclass.
        """
        response = self.client.get(f"customers/{customer_id}")
        response.raise_for_status()
        data = response.json()
        addr = data.get("address", {})

        return Customer(
            id=data["id"],
            first_name=data["firstName"],
            last_name=data["lastName"],
            address=Address(
                street=addr.get("street", ""),
                city=addr.get("city", ""),
                state=addr.get("state", ""),
                zip_code=addr.get("zipCode", ""),
            ),
            phone_number=data.get("phoneNumber", ""),
            ssn=data.get("ssn", ""),
        )

    def get_customer_id(self, username: str, password: str) -> int:
        """Login and return only the numeric customer ID.

        :param username: Customer username.
        :param password: Customer password.
        :returns: Positive integer customer ID.
        """
        data = self.login(username, password)

        return int(data["id"])
