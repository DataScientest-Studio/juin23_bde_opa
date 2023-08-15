from abc import ABC, abstractmethod

from opa.core.financial_data import (
    StockValue,
    StockValueType,
    StockValueKind,
    CompanyInfo,
    StockCollectionStats,
)


class Storage(ABC):
    @abstractmethod
    def insert_values(self, values: list[StockValue]):
        ...

    @abstractmethod
    def get_values(
        self, ticker: str, kind: StockValueKind, limit: int = 500
    ) -> list[StockValue]:
        ...

    @abstractmethod
    def get_all_tickers(self) -> list[str]:
        ...

    @abstractmethod
    def insert_company_infos(self, infos: list[CompanyInfo]):
        ...

    @abstractmethod
    def get_company_infos(self, tickers: list[str]) -> dict[str, CompanyInfo]:
        ...

    @abstractmethod
    def get_stats(self, type_: StockValueType) -> dict[str, StockCollectionStats]:
        ...
