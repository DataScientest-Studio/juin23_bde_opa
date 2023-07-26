from abc import ABC, abstractmethod

from opa.core import get_secret, StockValue, StockValueType


class StockMarketProvider(ABC):
    def __init__(self):
        self.access_key = get_secret(self.api_key_secret_file)

    @abstractmethod
    def get_stock_values(self, ticker: str, type_: StockValueType) -> list[StockValue]:
        ...

    def get_raw_stock_values(self, ticker: str, type_: StockValueType) -> dict:
        raise NotImplementedError()
