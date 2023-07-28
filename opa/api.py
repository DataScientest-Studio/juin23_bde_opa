from fastapi import FastAPI

from opa.core.financial_data import StockValue, StockValueType
from opa.storage import opa_storage


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tickers")
async def all_tickers() -> list[str]:
    return opa_storage.get_all_tickers()


@app.get("/{ticker}")
async def historical(ticker: str, type: StockValueType) -> list[StockValue]:
    return opa_storage.get_values(ticker, type)
