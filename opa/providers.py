import os
from abc import ABC, abstractmethod
from datetime import date, datetime

from pydantic import BaseModel

from opa.app_secrets import get_secret
from opa.http_methods import get_json_data


class StockMarketProvider(ABC):
    def __init__(self):
        self.access_key = get_secret(self.api_key_secret_file)

    def get_historical_data(self, ticker):
        raw = self.get_raw_historical_data(ticker)
        return self.into_historical_data(raw)

    def get_streaming_data(self, ticker):
        raw = self.get_raw_streaming_data(ticker)
        return self.into_streaming_data(raw)

    @abstractmethod
    def get_raw_historical_data(self, ticker):
        ...

    @staticmethod
    @abstractmethod
    def into_historical_data(data):
        ...

    @abstractmethod
    def get_raw_streaming_data(self, ticker):
        ...

    @staticmethod
    @abstractmethod
    def into_streaming_data(data):
        ...


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
