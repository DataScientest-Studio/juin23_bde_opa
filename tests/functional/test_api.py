import requests
import pytest


@pytest.fixture(scope="session", autouse=True)
def wait_for_server_availability():
    timeout = 5
    try:
        requests.get("http://internal_api:8000/", timeout=timeout)
    except requests.exceptions.ConnectionError:
        pytest.exit(f"API server could not be reached after {timeout}s")

    yield None


class TestApi:
    def test_get(self):
        r = requests.get("http://internal_api:8000/docs")
        assert r.status_code == 200


class TestTickers:
    def test_is_list(self):
        r = requests.get("http://internal_api:8000/tickers")
        assert isinstance(r.json(), list)
