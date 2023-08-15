from abc import abstractmethod
from datetime import datetime
from enum import Enum


from pydantic import BaseModel


class StockValueSerieGranularity(Enum):
    FINE = "fine"
    COARSE = "coarse"


class StockValueKind(Enum):
    SIMPLE = "simple"
    OHLC = "ohlc"


class StockValue(BaseModel):
    ticker: str
    date: datetime
    close: float
    interval: int
    open: float | None = None
    low: float | None = None
    high: float | None = None
    volume: int | None = None


class StockValueMixin:
    @abstractmethod
    def as_stock_value(self, **kwargs) -> StockValue:
        ...


class CompanyInfo(BaseModel):
    symbol: str
    name: str
    currency: str
    website: str
    description: str
    sector: str
    country: str
    image: str
    ipo_date: datetime
    address: str
    city: str


class CompanyInfoMixin:
    @abstractmethod
    def as_company_info(self, **kwargs) -> CompanyInfo:
        ...


class StockCollectionStats(BaseModel):
    latest: datetime
    oldest: datetime
    count: int
