from opa.providers import FmpCloud
from opa.storage import storage
from opa.core import StockValueType, FinancialDataReader


ALL_VALUES = ["AAPL", "MSFT", "AMZN", "GOOG", "META"]


if __name__ == "__main__":
    fmp = FmpCloud()
    reader = FinancialDataReader(fmp, storage)
    reader.import_company_info(ALL_VALUES)
    reader.import_stock_values(ALL_VALUES, StockValueType.HISTORICAL)
    reader.import_stock_values(ALL_VALUES, StockValueType.STREAMING)
