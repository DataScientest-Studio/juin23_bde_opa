from datetime import date, datetime, time

from pydantic import BaseModel

from opa import environment
from opa.http_methods import get_json_data
from opa.core.providers import StockMarketProvider
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

    def get_stock_values(self, ticker: str, type_: StockValueType) -> list[StockValue]:
        json = self.get_raw_stock_values(ticker, type_)
        return [
            v.as_stock_value(ticker=ticker)
            for v in self._as_validated_list_of_values(json, type_)
        ]

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

        data = get_json_data(
            f"https://fmpcloud.io/api/v3/profile/{tickers_as_str}",
            params={"apikey": self.access_key},
        )

        return [FmpCloudCompanyInfo(**v).as_company_info() for v in data]
