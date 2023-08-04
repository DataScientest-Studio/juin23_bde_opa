from loguru import logger

from opa.core import StockValueType, FinancialDataReader
from opa.providers import opa_provider
from opa.storage import opa_storage


ALL_VALUES = ["AAPL", "MSFT", "AMZN", "GOOG", "META"]


if __name__ == "__main__":
    logger.info("Reader app starting up...")
    reader = FinancialDataReader(opa_provider, opa_storage)

    reader.import_company_info(ALL_VALUES)
    reader.import_stock_values(ALL_VALUES, StockValueType.HISTORICAL)
    reader.import_stock_values(ALL_VALUES, StockValueType.STREAMING)

    logger.info("Reader app done")
