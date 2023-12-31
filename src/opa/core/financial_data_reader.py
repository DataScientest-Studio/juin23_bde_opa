from dataclasses import dataclass

from loguru import logger

from opa.core.financial_data import (
    StockValue,
    StockValueSerieGranularity,
    StockValueKind,
)
from opa.core.providers import StockMarketProvider
from opa.core.storage import Storage


@dataclass
class FinancialDataReader:
    provider: StockMarketProvider
    storage: Storage

    def run(self, tickers):
        self.import_company_info(tickers)
        self.import_stock_values(
            tickers,
            StockValueKind.SIMPLE,
            StockValueSerieGranularity.COARSE,
        )
        self.import_stock_values(
            tickers,
            StockValueKind.OHLC,
            StockValueSerieGranularity.FINE,
        )
        # Coarse-grained values are imported AFTER fine-grained values so that
        # fine-grained values are always stored in priority.
        self.import_stock_values(
            tickers,
            StockValueKind.OHLC,
            StockValueSerieGranularity.COARSE,
        )

    def import_company_info(self, tickers: list[str]):
        infos = self.provider.get_company_info(tickers)
        return self.storage.insert_company_infos(infos)

    def import_stock_values(
        self,
        tickers: list[str],
        kind: StockValueKind,
        granularity: StockValueSerieGranularity,
    ) -> list[StockValue]:
        # TODO: `storage.get_stats` should evolve to not make stats on data that has granularity
        # difference (ie take "interval" into account).
        stats = self.storage.get_stats(kind)

        api_values = {
            ticker: self.provider.get_stock_values(ticker, kind, granularity)
            for ticker in tickers
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
            self.storage.insert_values(all_new_values)
        else:
            logger.info(
                (
                    "{nb} '{kind}' {granularity}-grained values fetched by the reader were discarded because "
                    "they cover a timespan already present in the storage"
                ),
                nb=len([v for v_list in api_values.values() for v in v_list]),
                kind=kind.value,
                granularity=granularity.value,
            )

        return all_new_values
