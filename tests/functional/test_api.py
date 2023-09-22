import requests
import pytest

from opa import settings


@pytest.fixture(scope="session")
def api_host():
    return settings.api_host


@pytest.fixture(scope="session")
def credentials():
    return (
        settings.secrets.data_report_api_username,
        settings.secrets.data_report_api_password,
    )


@pytest.fixture(scope="session")
def actual_ticker():
    return "MSFT"


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
    def test_not_auth(self, api_host):
        r = requests.get(f"http://{api_host}:8000/tickers")
        assert r.status_code == 401

    def test_auth(self, api_host, credentials):
        r = requests.get(f"http://{api_host}:8000/tickers", auth=credentials)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestStockValues:
    def test_not_auth(self, api_host, actual_ticker):
        r = requests.get(f"http://{api_host}:8000/{actual_ticker}")
        assert r.status_code == 401

    def test_auth(
        self,
        api_host,
        actual_ticker,
        stock_value_kind,
        stock_value_serie_granularity,
        credentials,
    ):
        r = requests.get(
            f"http://{api_host}:8000/{actual_ticker}",
            params={
                "kind": stock_value_kind.value,
                "granularity": stock_value_serie_granularity.value,
            },
            auth=credentials,
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestCompanyInfo:
    def test_not_auth(self, api_host, actual_ticker):
        r = requests.get(f"http://{api_host}:8000/company_infos/{actual_ticker}")
        assert r.status_code == 401

    def test_auth(self, api_host, actual_ticker, credentials):
        r = requests.get(
            f"http://{api_host}:8000/company_infos/{actual_ticker}", auth=credentials
        )
        assert r.status_code == 200
        assert isinstance(r.json(), dict)


class TestCompanyInfos:
    def test_not_auth(self, api_host, actual_ticker):
        r = requests.get(
            f"http://{api_host}:8000/company_infos", params=[("tickers", actual_ticker)]
        )
        assert r.status_code == 401

    def test_auth(self, api_host, actual_ticker, credentials):
        r = requests.get(
            f"http://{api_host}:8000/company_infos",
            params=[("tickers", actual_ticker)],
            auth=credentials,
        )
        assert r.status_code == 200
        assert isinstance(r.json(), dict)
