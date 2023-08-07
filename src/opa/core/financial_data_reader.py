from dataclasses import dataclass

from loguru import logger

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
        stats = self.storage.get_stats(type_)

        api_values = {
            ticker: self.provider.get_stock_values(ticker, type_) for ticker in tickers
        }

        # Filter out all the values that are within the same time range as those
        # already stored
        new_values = {
            ticker: [
                v
                for v in v_list
                if ticker not in stats.keys()
                or v.date > stats[ticker].latest
                or v.date < stats[ticker].oldest
            ]
            for (ticker, v_list) in api_values.items()
        }

        # Flatten all the values
        all_new_values = [v for v_list in new_values.values() for v in v_list]
        if all_new_values:
            self.storage.insert_values(all_new_values, type_)
        else:
            logger.info(
                (
                    "{nb} '{type}' values fetched by the reader were discarded because "
                    "they cover a timespan already present in the storage"
                ),
                nb=len([v for v_list in api_values.values() for v in v_list]),
                type=type_.value,
            )

        return all_new_values
