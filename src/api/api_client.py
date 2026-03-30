import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ApiClient:
    """Thin wrapper around requests.Session for ParaBank REST API calls."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.session.verify = False
        self.timeout = timeout

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.base_url}/{path}", timeout=self.timeout, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(f"{self.base_url}/{path}", timeout=self.timeout, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.session.put(f"{self.base_url}/{path}", timeout=self.timeout, **kwargs)

    def close(self) -> None:
        self.session.close()
