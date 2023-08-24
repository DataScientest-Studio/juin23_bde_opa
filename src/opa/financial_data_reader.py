from loguru import logger

from opa.core import FinancialDataReader
from opa.providers import opa_provider
from opa.storage import opa_storage


if __name__ == "__main__":
    logger.info("Reader app starting up...")

    reader = FinancialDataReader(opa_provider, opa_storage)
    reader.run(["AAPL", "MSFT", "AMZN", "GOOG", "META"])

    logger.info("Reader app done")
