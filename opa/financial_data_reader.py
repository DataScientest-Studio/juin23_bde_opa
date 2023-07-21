from opa.providers import FmpCloud
from opa.storage import storage


if __name__ == "__main__":
    print("Hello from financial_data_reader")

    fmp = FmpCloud()

    historical = {
        ticker: fmp.get_historical_data(ticker)
        for ticker in ["AAPL", "MSFT", "AMZN", "GOOG", "META"]
    }

    all_values = [v for vals in historical.values() for v in vals]
    storage.insert_historical(all_values)
