import requests
import pytest

from opa import settings


@pytest.fixture(scope="session")
def api_host():
    return settings.api_host


@pytest.fixture(scope="session", autouse=True)
def wait_for_server_availability(api_host):
    timeout = 5
    try:
        requests.get(f"http://{api_host}:8000/", timeout=timeout)
    except requests.exceptions.ConnectionError:
        pytest.exit(f"API server could not be reached after {timeout}s")

    yield None


class TestDocs:
    def test_get(self, api_host):
        r = requests.get(f"http://{api_host}:8000/docs")
        assert r.status_code == 200


class TestTickers:
    def test_is_list(self, api_host):
        r = requests.get(f"http://{api_host}:8000/tickers")
        assert isinstance(r.json(), list)
