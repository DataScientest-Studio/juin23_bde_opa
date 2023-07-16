from providers import FmpCloud
import time
import os


print("Hello from financial_data_reader")
#StockMarketProvider()
fmp = FmpCloud()
print(fmp.get_historical_data("AAPL").historical[:10])
