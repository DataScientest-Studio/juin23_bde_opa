from providers import FmpCloud
from storage import insert_historical


if __name__ == "__main__":
    print("Hello from financial_data_reader")

    fmp = FmpCloud()

    historical = {
        ticker: fmp.get_historical_data(ticker)
        for ticker in ["AAPL", "MSFT", "AMZN", "GOOG", "META"]
    }

    for vals in historical.values():
        insert_historical(vals)
