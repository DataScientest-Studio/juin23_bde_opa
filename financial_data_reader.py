from providers import FmpCloud
from storage import insert_historical


if __name__ == "__main__":
    print("Hello from financial_data_reader")

    fmp = FmpCloud()
    historical = fmp.get_historical_data("AAPL")
    insert_historical(historical)
