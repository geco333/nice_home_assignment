from src.api.api_client import ApiClient
from src.models.customer import Customer, Address


class CustomerApi:
    """Operations against the /customers endpoints."""

    def __init__(self, client: ApiClient):
        self.client = client

    def login(self, username: str, password: str) -> dict:
        response = self.client.get(f"login/{username}/{password}")
        response.raise_for_status()

        return response.json()

    def get_customer(self, customer_id: int) -> Customer:
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
        data = self.login(username, password)
        
        return int(data["id"])
