from abc import ABC, abstractmethod

from opa.financial_data import StockValue, StockValueType


class Storage(ABC):
    @abstractmethod
    def insert_values(self, values: list[StockValue], type_: StockValueType):
        ...

    @abstractmethod
    def get_values(
        self, ticker: str, type_: StockValueType, limit: int = 500
    ) -> list[StockValue]:
        ...

    @abstractmethod
    def get_all_tickers(self) -> list[str]:
        ...
