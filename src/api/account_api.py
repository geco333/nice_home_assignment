import subprocess
import json

from src.api.api_client import ApiClient
from src.models.account import Account, AccountType


class AccountApi:
    """Operations against the /accounts and /customers/.../accounts endpoints."""

    def __init__(self, client: ApiClient):
        self.client = client

    def get_customer_accounts(self, customer_id: int) -> list[Account]:
        response = self.client.get(f"customers/{customer_id}/accounts")
        response.raise_for_status()
        data = response.json()
        return [
            Account(
                id=acc["id"],
                customer_id=acc["customerId"],
                type=acc["type"],
                balance=float(acc["balance"]),
            )
            for acc in data
        ]

    def get_account(self, account_id: int) -> Account:
        response = self.client.get(f"accounts/{account_id}")
        response.raise_for_status()
        data = response.json()
        return Account(
            id=data["id"],
            customer_id=data["customerId"],
            type=data["type"],
            balance=float(data["balance"]),
        )

    def create_account_via_curl(
        self,
        customer_id: int,
        new_account_type: AccountType,
        from_account_id: int,
    ) -> Account:
        """Create a new account using a curl command as required by the assignment."""
        url = (
            f"{self.client.base_url}/createAccount"
            f"?customerId={customer_id}"
            f"&newAccountType={new_account_type.value}"
            f"&fromAccountId={from_account_id}"
        )
        result = subprocess.run(
            [
                "curl", "-s", "-k",
                "-X", "POST",
                "-H", "Accept: application/json",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"curl failed (rc={result.returncode}): {result.stderr}")

        data = json.loads(result.stdout)
        return Account(
            id=data["id"],
            customer_id=data["customerId"],
            type=data["type"],
            balance=float(data["balance"]),
        )

    def transfer_funds(self, from_account_id: int, to_account_id: int, amount: float) -> dict:
        response = self.client.post(
            f"transfer?fromAccountId={from_account_id}&toAccountId={to_account_id}&amount={amount}"
        )
        response.raise_for_status()
        return {"status_code": response.status_code, "message": response.text}
