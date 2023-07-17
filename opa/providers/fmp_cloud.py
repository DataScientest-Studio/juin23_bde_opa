from datetime import date, datetime

from pydantic import BaseModel

from opa.http_methods import get_json_data
from opa.providers import StockMarketProvider


class FmpCloudHistoricalValue(BaseModel):
    date: date
    close: float


class FmpCloudHistoricalData(BaseModel):
    symbol: str
    historical: list[FmpCloudHistoricalValue]


class FmpCloudStreamingValue(BaseModel):
    date: datetime
    open: float
    close: float
    low: float
    high: float
    volume: int


class FmpCloud(StockMarketProvider):
    api_key_secret_file = "fmp_cloud_api_key"

    def get_raw_historical_data(self, ticker):
        return get_json_data(
            f"https://fmpcloud.io/api/v3/historical-price-full/{ticker}",
            params={"serietype": "line", "apikey": self.access_key},
        )

    @staticmethod
    def into_historical_data(data):
        return FmpCloudHistoricalData(**data)


    def get_raw_streaming_data(self, ticker):
        return get_json_data(
            f"https://fmpcloud.io/api/v3/historical-chart/15min/{ticker}",
            params={"apikey": self.access_key},
        )

    @staticmethod
    def into_streaming_data(data):
        return [FmpCloudStreamingValue(**v) for v in data]
