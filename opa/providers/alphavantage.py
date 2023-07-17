from opa.http_methods import get_json_data
from opa.providers import StockMarketProvider


class Alphavantage(StockMarketProvider):
    """
    Validation functions are not implemented for this module because this provider
    will remain unused.
    """

    api_key_secret_file = "alphavantage_api_key"

    def get_raw_historical_data(self, ticker):
        # Documentation available here: https://www.alphavantage.co/documentation/#dailyadj
        return get_json_data(
            f"https://www.alphavantage.co/query",
            params={
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": ticker,
                "apikey": self.access_key,
            },
        )

    def get_raw_streaming_data(self, ticker):
        # Documentation available here: https://www.alphavantage.co/documentation/#intraday
        return get_json_data(
            f"https://www.alphavantage.co/query",
            params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": ticker,
                "interval": "15min",
                "apikey": self.access_key,
            },
        )

    @staticmethod
    def into_historical_data(data):
        raise NotImplementedError()

    @staticmethod
    def into_streaming_data(data):
        raise NotImplementedError()
