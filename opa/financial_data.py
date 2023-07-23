from abc import abstractmethod
from datetime import datetime


from pydantic import BaseModel


class StockValue(BaseModel):
    ticker: str
    date: datetime
    close: float
    open: float | None = None
    low: float | None = None
    high: float | None = None
    volume: int | None = None


class StockValueMixin:
    @abstractmethod
    def as_stock_value(self, **kwargs) -> StockValue:
        ...
