from loguru import logger

from opa.core import FinancialDataReader
from opa.providers import opa_provider
from opa.storage import opa_storage
from opa.config import settings


if __name__ == "__main__":
    logger.info("Reader app starting up...")

    reader = FinancialDataReader(opa_provider, opa_storage)
    reader.run(settings.tickers_list)

    logger.info("Reader app done")
