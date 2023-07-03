"""
An example of code to make calls onto stock market providers.

The secret API keys are pulled from a `.env` file using `dotenv`. They can also
be passed into the OS environment via e.g. `export FMPCLOUD_KEY=xxx`.
"""


import os
import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    ...


http_session = requests.Session()


def get_json_data(url: str, **kwargs):
    http = http_session.get(url, **kwargs)
    return http.json()


class StockMarketProvider:
    def __init__(self):
        self.access_key = os.getenv(self.secret_key)

    def get_historical_data(self, ticker):
        raise NotImplementedError

    def get_streaming_data(self, ticker):
        raise NotImplementedError


class FmpCloud(StockMarketProvider):
    secret_key = "FMPCLOUD_KEY"

    def get_historical_data(self, ticker):
        return get_json_data(
            f"https://fmpcloud.io/api/v3/historical-price-full/{ticker}",
            params={"serietype": "line", "apikey": self.access_key},
        )

    def get_streaming_data(self, ticker):
        return get_json_data(
            f"https://fmpcloud.io/api/v3/historical-chart/15min/{ticker}",
            params={"apikey": self.access_key},
        )


class Alphavantage(StockMarketProvider):
    secret_key = "ALPHAVANTAGE_KEY"

    def get_streaming_data(self, ticker):
        return get_json_data(
            f"https://www.alphavantage.co/query",
            params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": ticker,
                "apikey": self.access_key,
            },
        )


class MarketStack(StockMarketProvider):
    secret_key = "MARKET_STACK_KEY"

    def get_streaming_data(self, ticker):
        return get_json_data(
            f"http://api.marketstack.com/v1/eod",
            params={
                "symbols": ticker,
                "access_key": self.access_key,
            },
        )
