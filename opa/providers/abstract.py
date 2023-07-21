from abc import ABC, abstractmethod

from opa.app_secrets import get_secret
from opa.financial_data import StockValue


class StockMarketProvider(ABC):
    def __init__(self):
        self.access_key = get_secret(self.api_key_secret_file)

    @abstractmethod
    def get_historical_data(self, ticker: str) -> list[StockValue]:
        ...

    @abstractmethod
    def get_streaming_data(self, ticker: str) -> list[StockValue]:
        ...

    def get_raw_historical_data(self, ticker) -> dict:
        raise NotImplementedError()

    def get_raw_streaming_data(self, ticker) -> dict:
        raise NotImplementedError()
