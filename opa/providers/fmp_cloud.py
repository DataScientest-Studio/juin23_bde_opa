from datetime import date, datetime, time

from pydantic import BaseModel

from opa.http_methods import get_json_data
from opa.providers import StockMarketProvider
from opa.financial_data import StockValue, StockValueMixin, StockValueType


class FmpCloudHistoricalValue(BaseModel, StockValueMixin):
    date: date
    close: float

    def as_stock_value(self, **kwargs) -> StockValue:
        ticker = kwargs.pop("ticker")
        return StockValue(
            ticker=ticker, date=datetime.combine(self.date, time.min), close=self.close
        )


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
            ticker=ticker,
            date=self.date,
            close=self.close,
            open=self.open,
            low=self.low,
            high=self.high,
            volume=self.volume,
        )


class FmpCloud(StockMarketProvider):
    api_key_secret_file = "fmp_cloud_api_key"

    def get_stock_values(self, ticker: str, type_: StockValueType) -> list[StockValue]:
        json = self.get_raw_stock_values(ticker, type_)

        match type_:
            case StockValueType.HISTORICAL:
                validated = FmpCloudHistoricalData(**json)
                return [v.as_stock_value(ticker=ticker) for v in validated.historical]

            case StockValueType.STREAMING:
                validated = [FmpCloudStreamingValue(**v) for v in json]
                return [v.as_stock_value(ticker=ticker) for v in validated]

            case _:
                raise TypeError(f"type should be a StockValueType, got {type_}")

    def get_raw_stock_values(self, ticker: str, type_: StockValueType) -> dict:
        match type_:
            case StockValueType.HISTORICAL:
                return get_json_data(
                    f"https://fmpcloud.io/api/v3/historical-price-full/{ticker}",
                    params={"serietype": "line", "apikey": self.access_key},
                )

            case StockValueType.STREAMING:
                return get_json_data(
                    f"https://fmpcloud.io/api/v3/historical-chart/15min/{ticker}",
                    params={"apikey": self.access_key},
                )

            case _:
                raise TypeError(f"type should be a StockValueType, got {type_}")
