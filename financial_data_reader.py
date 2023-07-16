from providers import FmpCloud


if __name__ == "__main__":
    print("Hello from financial_data_reader")

    fmp = FmpCloud()
    print(fmp.get_historical_data("AAPL").historical[:10])
