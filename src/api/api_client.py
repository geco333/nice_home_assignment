"""Thin HTTP client wrapping ``requests.Session`` for ParaBank REST API calls."""
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ApiClient:
    """Reusable HTTP client for the ParaBank REST API.

    Configures a ``requests.Session`` with JSON Accept headers and
    TLS verification disabled (ParaBank uses a self-signed certificate).
    """

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize the API client.

        :param base_url: Root URL of the ParaBank API (e.g. ``https://parabank.parasoft.com/parabank/services/bank``).
        :param timeout: Default request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.session.verify = False
        self.timeout = timeout

    def get(self, path: str, **kwargs) -> requests.Response:
        """Send a GET request to ``{base_url}/{path}``.

        :param path: API endpoint path.
        :returns: Response object.
        """
        return self.session.get(f"{self.base_url}/{path}", timeout=self.timeout, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        """Send a POST request to ``{base_url}/{path}``.

        :param path: API endpoint path.
        :returns: Response object.
        """
        return self.session.post(f"{self.base_url}/{path}", timeout=self.timeout, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        """Send a PUT request to ``{base_url}/{path}``.

        :param path: API endpoint path.
        :returns: Response object.
        """
        return self.session.put(f"{self.base_url}/{path}", timeout=self.timeout, **kwargs)

    def close(self) -> None:
        """Close the underlying HTTP session and release connections."""
        self.session.close()
