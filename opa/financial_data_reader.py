from opa.financial_data import StockValue
from opa.providers import StockMarketProvider, FmpCloud
from opa.storage import storage


ALL_VALUES = ["AAPL", "MSFT", "AMZN", "GOOG", "META"]


def retrieve_data_and_store(
    provider: StockMarketProvider, tickers: list[str]
) -> list[StockValue]:
    values = [
        stock_value
        for ticker in tickers
        for stock_value in provider.get_historical_data(ticker)
    ]
    storage.insert_historical(values)
    return values


if __name__ == "__main__":
    print("Hello from financial_data_reader")

    fmp = FmpCloud()
    retrieve_data_and_store(fmp, ALL_VALUES)
