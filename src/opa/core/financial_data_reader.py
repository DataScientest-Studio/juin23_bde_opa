from dataclasses import dataclass

from opa.core.financial_data import StockValue, StockValueType
from opa.core.providers import StockMarketProvider
from opa.core.storage import Storage


@dataclass
class FinancialDataReader:
    provider: StockMarketProvider
    storage: Storage

    def import_company_info(self, tickers: list[str]):
        infos = self.provider.get_company_info(tickers)
        return self.storage.insert_company_infos(infos)

    def import_stock_values(
        self, tickers: list[str], type_: StockValueType
    ) -> list[StockValue]:
        values = [
            stock_value
            for ticker in tickers
            for stock_value in self.provider.get_stock_values(ticker, type_)
        ]
        self.storage.insert_values(values, type_)
        return values
