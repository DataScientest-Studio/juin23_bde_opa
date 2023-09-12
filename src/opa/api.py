import secrets
import json
import base64
from hashlib import scrypt
from typing import Annotated, Optional

from loguru import logger
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from opa.core.financial_data import StockValue, StockValueKind, CompanyInfo
from opa.storage import opa_storage


logger.info("API app starting up...")

app = FastAPI()
security = HTTPBasic()


def encrypt_pass(password):
    c = scrypt(password, n=2, r=3, p=5, salt=b"salt")
    return base64.b64encode(c).decode("ascii")


creds_file = "app_data/secrets/creds.json"


def read_creds():
    with open(creds_file) as f:
        return json.load(f)


def auth_user(username, password):
    all_users = {"bob": encrypt_pass(b"pouet")}
    with open(creds_file, "w") as f:
        json.dump(all_users, f)

    expected_password = all_users.get(username)
    if expected_password:
        if secrets.compare_digest(expected_password, encrypt_pass(password.encode())):
            return True

    print("Bad credentials")
    return False


def check_user(credentials: HTTPBasicCredentials):
    if not auth_user(credentials.username, credentials.password):
        raise HTTPException(401, "Bad credentials")


@app.get("/")
async def root(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    check_user(credentials)
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
