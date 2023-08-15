from datetime import date, datetime, time
from pathlib import Path

from pydantic import BaseModel
from loguru import logger

from opa import settings
from opa.http_methods import get_json_data
from opa.core.providers import StockMarketProvider
from opa.core.financial_data import (
    StockValue,
    StockValueMixin,
    CompanyInfo,
    CompanyInfoMixin,
    StockValueSerieGranularity,
    StockValueKind,
)


class FmpCloudSimpleValue(BaseModel, StockValueMixin):
    date: date
    close: float

    def as_stock_value(self, **kwargs) -> StockValue:
        ticker = kwargs.pop("ticker")
        return StockValue(
            ticker=ticker,
            date=datetime.combine(self.date, time.min),
            close=self.close,
            interval=24 * 60 * 60,
        )


class FmpCloudSimpleData(BaseModel):
    symbol: str
    historical: list[FmpCloudSimpleValue]


class FmpCloudOhlcValue(BaseModel, StockValueMixin):
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
            interval=15 * 60,
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
        self.access_key = settings.secrets.fmp_cloud_api_key

    def get_stock_values(
        self,
        ticker: str,
        kind: StockValueKind,
        granularity: StockValueSerieGranularity,
    ) -> list[StockValue]:
        json = self.get_raw_stock_values(ticker, kind, granularity)
        ret = [
            v.as_stock_value(ticker=ticker)
            for v in self._as_validated_list_of_values(json, kind, granularity)
        ]

        logger.info(
            "Fetched {count} {kind} {granularity}-grained stock values",
            count=len(ret),
            kind=kind.value,
            granularity=granularity.value,
        )
        return ret

    def get_raw_stock_values(
        self,
        ticker: str,
        kind: StockValueKind,
        granularity: StockValueSerieGranularity,
    ) -> dict:
        match (kind, granularity):
            case (StockValueKind.SIMPLE, StockValueSerieGranularity.COARSE):
                return self._get_json_data(
                    f"/historical-price-full/{ticker}",
                    serietype="line",
                )

            case (StockValueKind.OHLC, StockValueSerieGranularity.FINE):
                return self._get_json_data(f"/historical-chart/15min/{ticker}")

            case _:
                raise TypeError(
                    f"This provider cannot provide ({kind, granularity}) stock values"
                )

    @staticmethod
    def _as_validated_list_of_values(
        json, kind: StockValueKind, granularity: StockValueSerieGranularity
    ) -> list[FmpCloudSimpleValue] | list[FmpCloudOhlcValue]:
        match (kind, granularity):
            case (StockValueKind.SIMPLE, StockValueSerieGranularity.COARSE):
                return FmpCloudSimpleData(**json).historical

            case (StockValueKind.OHLC, StockValueSerieGranularity.FINE):
                return [FmpCloudOhlcValue(**v) for v in json]

            case _:
                raise TypeError(f"cannot validate ({kind, granularity}) stock values")

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
