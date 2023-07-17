from abc import ABC, abstractmethod

from opa.app_secrets import get_secret


class StockMarketProvider(ABC):
    def __init__(self):
        self.access_key = get_secret(self.api_key_secret_file)

    def get_historical_data(self, ticker: str):
        raw = self.get_raw_historical_data(ticker)
        return self.into_historical_data(raw)

    def get_streaming_data(self, ticker: str):
        raw = self.get_raw_streaming_data(ticker)
        return self.into_streaming_data(raw)

    @abstractmethod
    def get_raw_historical_data(self, ticker):
        ...

    @staticmethod
    @abstractmethod
    def into_historical_data(data):
        ...

    @abstractmethod
    def get_raw_streaming_data(self, ticker):
        ...

    @staticmethod
    @abstractmethod
    def into_streaming_data(data):
        ...
