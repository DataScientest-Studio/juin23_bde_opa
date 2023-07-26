from opa.core.financial_data import StockValue, StockValueType
from opa.core.providers import StockMarketProvider
from opa.providers import FmpCloud
from opa.storage import storage


ALL_VALUES = ["AAPL", "MSFT", "AMZN", "GOOG", "META"]


def retrieve_data_and_store(
    provider: StockMarketProvider, tickers: list[str], type_: StockValueType
) -> list[StockValue]:
    values = [
        stock_value
        for ticker in tickers
        for stock_value in provider.get_stock_values(ticker, type_)
    ]
    storage.insert_values(values, type_)
    return values


if __name__ == "__main__":
    print("Hello from financial_data_reader")

    fmp = FmpCloud()
    retrieve_data_and_store(fmp, ALL_VALUES, StockValueType.HISTORICAL)
    retrieve_data_and_store(fmp, ALL_VALUES, StockValueType.STREAMING)
