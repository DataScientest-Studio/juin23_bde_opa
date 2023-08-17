from loguru import logger

from opa.core import (
    FinancialDataReader,
    StockValueSerieGranularity,
    StockValueKind,
)
from opa.providers import opa_provider
from opa.storage import opa_storage


ALL_VALUES = ["AAPL", "MSFT", "AMZN", "GOOG", "META"]


if __name__ == "__main__":
    logger.info("Reader app starting up...")
    reader = FinancialDataReader(opa_provider, opa_storage)

    reader.import_company_info(ALL_VALUES)
    reader.import_stock_values(
        ALL_VALUES,
        StockValueKind.SIMPLE,
        StockValueSerieGranularity.COARSE,
    )
    reader.import_stock_values(
        ALL_VALUES,
        StockValueKind.OHLC,
        StockValueSerieGranularity.FINE,
    )
    # Coarse-grained values are imported AFTER fine-grained values so that
    # fine-grained values are always stored in priority.
    reader.import_stock_values(
        ALL_VALUES,
        StockValueKind.OHLC,
        StockValueSerieGranularity.COARSE,
    )

    logger.info("Reader app done")
