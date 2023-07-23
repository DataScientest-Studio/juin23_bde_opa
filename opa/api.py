from fastapi import FastAPI
import os

from opa.storage import storage


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tickers")
async def all_tickers():
    return storage.get_all_tickers()


@app.get("/{ticker}/historical")
async def historical(ticker: str):
    return storage.get_historical(ticker)
