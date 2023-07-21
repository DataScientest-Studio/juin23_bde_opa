from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class StockValue:
    ticker: str
    date: datetime
    close: float
    open: Optional[float] = None
    low: Optional[float] = None
    high: Optional[float] = None
    volume: Optional[int] = None


class StockValueMixin:
    @abstractmethod
    def as_stock_value(self, **kwargs) -> StockValue:
        ...
