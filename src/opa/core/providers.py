from abc import ABC, abstractmethod

from opa.core import (
    StockValue,
    CompanyInfo,
    StockValueSerieGranularity,
    StockValueKind,
)


class StockMarketProvider(ABC):
    @abstractmethod
    def get_stock_values(
        self,
        ticker: str,
        kind: StockValueKind,
        granularity: StockValueSerieGranularity,
    ) -> list[StockValue]:
        ...

    def get_raw_stock_values(
        self,
        ticker: str,
        kind: StockValueKind,
        granularity: StockValueSerieGranularity,
    ) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def get_company_info(self, tickers: list[str]) -> list[CompanyInfo]:
        ...
