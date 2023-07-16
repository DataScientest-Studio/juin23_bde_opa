import os
from abc import ABC, abstractmethod
from datetime import date

from pydantic import BaseModel

from app_secrets import get_secret
from http_methods import get_json_data


class StockMarketProvider(ABC):
    def __init__(self):
        self.access_key = get_secret(self.api_key_secret_file)

    @abstractmethod
    def get_historical_data(self, ticker):
        ...

    @abstractmethod
    def get_streaming_data(self, ticker):
        ...


class FmpCloudHistoricalValue(BaseModel):
    date: date
    close: float


class FmpCloudHistoricalData(BaseModel):
    symbol: str
    historical: list[FmpCloudHistoricalValue]


class FmpCloud(StockMarketProvider):
    api_key_secret_file = "fmp_cloud_api_key"

    def get_historical_data(self, ticker):
        json = get_json_data(
            f"https://fmpcloud.io/api/v3/historical-price-full/{ticker}",
            params={"serietype": "line", "apikey": self.access_key},
        )
        return FmpCloudHistoricalData(**json)

    def get_streaming_data(self, ticker):
        return get_json_data(
            f"https://fmpcloud.io/api/v3/historical-chart/15min/{ticker}",
            params={"apikey": self.access_key},
        )
