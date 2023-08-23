from typing import Annotated, Optional

from loguru import logger
from fastapi import FastAPI, Query

from opa.core.financial_data import StockValue, StockValueKind, CompanyInfo
from opa.storage import opa_storage


logger.info("API app starting up...")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/tickers")
async def all_tickers() -> list[str]:
    return opa_storage.get_all_tickers()


@app.get("/company_infos/{ticker}")
async def get_company_info(ticker: str) -> CompanyInfo:
    """Get information from one specific company"""
    return opa_storage.get_company_infos([ticker])[ticker]


@app.get("/company_infos")
async def get_company_infos(
    tickers: Annotated[list[str], Query()]
) -> dict[str, CompanyInfo]:
    """Get information from a list of companies"""
    return opa_storage.get_company_infos(tickers)


@app.get("/{ticker}")
async def get_stock_values(
    ticker: str, kind: StockValueKind, limit: Optional[int] = None
) -> list[StockValue]:
    kwargs = {}
    if limit is not None:
        kwargs |= dict(limit=limit)

    return opa_storage.get_values(ticker, kind, **kwargs)
