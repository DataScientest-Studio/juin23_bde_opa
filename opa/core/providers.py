from abc import ABC, abstractmethod

from opa.core import StockValue, StockValueType, CompanyInfo


class StockMarketProvider(ABC):
    @abstractmethod
    def get_stock_values(self, ticker: str, type_: StockValueType) -> list[StockValue]:
        ...

    def get_raw_stock_values(self, ticker: str, type_: StockValueType) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def get_company_info(self, tickers: list[str]) -> list[CompanyInfo]:
        ...
