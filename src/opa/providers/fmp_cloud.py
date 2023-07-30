from datetime import date, datetime, time
from pathlib import Path
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from loguru import logger

from opa import environment
from opa.http_methods import get_json_data
from opa.core.providers import StockMarketProvider, TimeRangeSpecifier
from opa.core.financial_data import (
    StockValue,
    StockValueMixin,
    StockValueType,
    CompanyInfo,
    CompanyInfoMixin,
)


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


class FmpCloudCompanyInfo(BaseModel, CompanyInfoMixin):
    symbol: str
    companyName: str
    currency: str
    website: str
    description: str
    sector: str
    country: str
    image: str
    ipoDate: date
    address: str
    city: str

    def as_company_info(self, **kwargs) -> CompanyInfo:
        return CompanyInfo(
            symbol=self.symbol,
            name=self.companyName,
            currency=self.currency,
            website=self.website,
            description=self.description,
            sector=self.sector,
            country=self.country,
            image=self.image,
            ipo_date=datetime.combine(self.ipoDate, time.min),
            address=self.address,
            city=self.city,
        )


class FmpCloud(StockMarketProvider):
    def __init__(self):
        self.access_key = environment.get_secret("fmp_cloud_api_key")

    def get_stock_values(
        self,
        ticker: str,
        type_: StockValueType,
        time_range: TimeRangeSpecifier = (None, None),
    ) -> list[StockValue]:
        json = self.get_raw_stock_values(ticker, type_, time_range)
        ret = [
            v.as_stock_value(ticker=ticker)
            for v in self._as_validated_list_of_values(json, type_)
        ]

        logger.info(
            "Fetched {count} {type_} stock values", count=len(ret), type_=type_.value
        )
        return ret

    def get_raw_stock_values(
        self,
        ticker: str,
        type_: StockValueType,
        time_range: TimeRangeSpecifier = (None, None),
    ) -> dict:
        date_range = self._get_date_range_params(time_range)

        match type_:
            case StockValueType.HISTORICAL:
                return self._get_json_data(
                    f"/historical-price-full/{ticker}", serietype="line", **date_range
                )

            case StockValueType.STREAMING:
                return self._get_json_data(
                    f"/historical-chart/15min/{ticker}", **date_range
                )

            case _:
                raise TypeError(f"type should be a StockValueType, got {type_}")

    @staticmethod
    def _get_date_range_params(range: TimeRangeSpecifier) -> dict:
        match range:
            case (None, None):
                return {}
            case (None, to_):
                return {"to": to_}
            case (from_, None):
                return {"from": from_}
            case (from_, to_):
                return {"from": from_, "to": to_}

    @staticmethod
    def _as_validated_list_of_values(
        json, type_
    ) -> list[FmpCloudHistoricalValue] | list[FmpCloudStreamingValue]:
        match type_:
            case StockValueType.HISTORICAL:
                return FmpCloudHistoricalData(**json).historical

            case StockValueType.STREAMING:
                return [FmpCloudStreamingValue(**v) for v in json]

            case _:
                raise TypeError(f"type should be a StockValueType, got {type_}")

    def get_company_info(self, tickers: list[str]) -> list[CompanyInfo]:
        # This part is sorted so that getting info for the same list of tickers always
        # yields the exact same HTTP request.
        tickers_as_str = ",".join(sorted(tickers))

        data = self._get_json_data(f"/profile/{tickers_as_str}")

        ret = [FmpCloudCompanyInfo(**v).as_company_info() for v in data]
        logger.info("Fetched company info for {} companies", len(ret))
        return ret

    def _get_json_data(self, path: str, **params):
        path = path[1:] if path.startswith("/") else path
        url = f"https://fmpcloud.io/api/v3/{path}"
        params = params | {"apikey": self.access_key}
        return get_json_data(str(url), params=params)
