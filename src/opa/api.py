from typing import Annotated, Optional

from loguru import logger
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from opa.core.financial_data import StockValue, StockValueKind, CompanyInfo
from opa.storage import opa_storage
from opa.auth import opa_auth


logger.info("API app starting up...")

app = FastAPI()
security = HTTPBasic()
CredentialsType = Annotated[HTTPBasicCredentials, Depends(security)]


def check_user(credentials: HTTPBasicCredentials):
    if not opa_auth.auth_user(credentials.username, credentials.password):
        raise HTTPException(401, "Bad credentials")


@app.get("/tickers")
async def all_tickers(credentials: CredentialsType) -> list[str]:
    check_user(credentials)
    return opa_storage.get_all_tickers()


@app.get("/company_infos/{ticker}")
async def get_company_info(ticker: str, credentials: CredentialsType) -> CompanyInfo:
    """Get information from one specific company"""
    check_user(credentials)
    return opa_storage.get_company_infos([ticker])[ticker]


@app.get("/company_infos")
async def get_company_infos(
    tickers: Annotated[list[str], Query()], credentials: CredentialsType
) -> dict[str, CompanyInfo]:
    """Get information from a list of companies"""
    check_user(credentials)
    return opa_storage.get_company_infos(tickers)


@app.get("/{ticker}")
async def get_stock_values(
    ticker: str,
    kind: StockValueKind,
    credentials: CredentialsType,
    limit: Optional[int] = None,
) -> list[StockValue]:
    check_user(credentials)

    kwargs = {}
    if limit is not None:
        kwargs |= dict(limit=limit)

    return opa_storage.get_values(ticker, kind, **kwargs)
