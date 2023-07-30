from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Optional, Tuple, Union

from opa.core import StockValue, StockValueType, CompanyInfo


TimeRangeBoundary = Union[str, datetime, date]
TimeRangeSpecifier = Tuple[Optional[TimeRangeBoundary], Optional[TimeRangeBoundary]]


class StockMarketProvider(ABC):
    @abstractmethod
    def get_stock_values(
        self,
        ticker: str,
        type_: StockValueType,
        time_range: TimeRangeSpecifier = (None, None)
    ) -> list[StockValue]:
        ...

    def get_raw_stock_values(
        self,
        ticker: str,
        type_: StockValueType,
        time_range: TimeRangeSpecifier = (None, None)
    ) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def get_company_info(self, tickers: list[str]) -> list[CompanyInfo]:
        ...
