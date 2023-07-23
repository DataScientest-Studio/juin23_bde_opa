from fastapi import FastAPI
import os

from opa.financial_data import StockValue
from opa.storage import storage


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tickers")
async def all_tickers() -> list[str]:
    return storage.get_all_tickers()


@app.get("/{ticker}/historical")
async def historical(ticker: str) -> list[StockValue]:
    return storage.get_historical(ticker)
