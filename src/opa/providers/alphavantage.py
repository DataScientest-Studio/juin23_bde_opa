from opa import settings
from opa.core import CompanyInfo
from opa.http_methods import get_json_data
from opa.core.financial_data import StockValue, StockValueType
from opa.core.providers import StockMarketProvider


class Alphavantage(StockMarketProvider):
    """
    Validation functions are not implemented for this module because this provider
    will remain unused.
    """

    def __init__(self):
        self.access_key = settings.secrets.alphavantage_api_key

    def get_stock_values(self, ticker: str, type_: StockValueType) -> list[StockValue]:
        raise NotImplementedError()

    def get_company_info(self, tickers: list[str]) -> list[CompanyInfo]:
        raise NotImplementedError()

    def get_raw_stock_values(self, ticker: str, type_: StockValueType) -> dict:
        match type_:
            case StockValueType.HISTORICAL:
                # Documentation available here: https://www.alphavantage.co/documentation/#dailyadj
                return self._get_json_data(
                    function="TIME_SERIES_DAILY_ADJUSTED",
                    symbol=ticker,
                )

            case StockValueType.STREAMING:
                # Documentation available here: https://www.alphavantage.co/documentation/#intraday
                return self._get_json_data(
                    function="TIME_SERIES_INTRADAY",
                    symbol=ticker,
                    interval="15min",
                )

    def _get_json_data(self, **params):
        params = params | {"apikey": self.access_key}
        return get_json_data("https://www.alphavantage.co/query", params=params)
