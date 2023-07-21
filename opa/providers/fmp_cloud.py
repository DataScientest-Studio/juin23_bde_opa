from datetime import date, datetime, time

from pydantic import BaseModel

from opa.http_methods import get_json_data
from opa.providers import StockMarketProvider
from opa.financial_data import StockValue, StockValueMixin


class FmpCloudHistoricalValue(BaseModel, StockValueMixin):
    date: date
    close: float

    def as_stock_value(self, **kwargs) -> StockValue:
        ticker = kwargs.pop("ticker")
        return StockValue(ticker, datetime.combine(self.date, time.min), self.close)


class FmpCloudHistoricalData(BaseModel):
    symbol: str
    historical: list[FmpCloudHistoricalValue]


class FmpCloudStreamingValue(BaseModel, StockValueMixin):
    date: datetime
    open: float
    close: float
    low: float
    high: float
    volume: int

    def as_stock_value(self, **kwargs) -> StockValue:
        ticker = kwargs.pop("ticker")
        return StockValue(
            ticker,
            datetime.combine(self.date, time.min),
            self.close,
            self.open,
            self.low,
            self.high,
            self.volume,
        )


class FmpCloud(StockMarketProvider):
    api_key_secret_file = "fmp_cloud_api_key"

    def get_historical_data(self, ticker) -> list[StockValue]:
        json = self.get_raw_historical_data(ticker)
        validated = FmpCloudHistoricalData(**json)
        return [v.as_stock_value(ticker=ticker) for v in validated.historical]

    def get_raw_historical_data(self, ticker) -> dict:
        return get_json_data(
            f"https://fmpcloud.io/api/v3/historical-price-full/{ticker}",
            params={"serietype": "line", "apikey": self.access_key},
        )

    def get_streaming_data(self, ticker: str) -> list[StockValue]:
        json = self.get_raw_streaming_data(ticker)
        validated = [FmpCloudStreamingValue(**v) for v in json]
        return [v.as_stock_value(ticker=ticker) for v in validated]

    def get_raw_streaming_data(self, ticker) -> dict:
        return get_json_data(
            f"https://fmpcloud.io/api/v3/historical-chart/15min/{ticker}",
            params={"apikey": self.access_key},
        )
