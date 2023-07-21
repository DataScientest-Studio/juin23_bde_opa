import datetime as dt
from abc import ABC, abstractmethod
from typing import Any

from pymongo import MongoClient
from pymongo.errors import BulkWriteError

from opa.app_secrets import get_secret
from opa.utils import is_running_in_docker
from opa.financial_data import StockValue


class Storage(ABC):
    @abstractmethod
    def insert_historical(self, historical: list[StockValue]):
        ...

    @abstractmethod
    def get_historical(self, ticker: str, limit: int = 500) -> list[StockValue]:
        ...


class MongoDbStorage(Storage):
    def __init__(self, uri: str) -> None:
        client: MongoClient = MongoClient(uri)

        self.db = client.get_database("stock_market")
        self.collections = {
            coll: self.db.get_collection(coll) for coll in ["historical", "streaming"]
        }

    def insert_historical(self, historical: list[StockValue]):
        insertable = [
            {k: v for (k, v) in h.__dict__.items() if v is not None} for h in historical
        ]
        try:
            # `ordered=False` ensures that at least some data will be inserted even if there are errors
            return self.collections["historical"].insert_many(insertable, ordered=False)
        except BulkWriteError as err:
            error_codes = {e["code"] for e in err.details["writeErrors"]}

            if error_codes == set([121]):
                print("ERROR: all records failed validation")

    def get_historical(self, ticker: str, limit: int = 500) -> list[StockValue]:
        return [
            StockValue(ticker=ticker, date=d["date"], close=d["close"])
            for d in self.collections["historical"].find(
                {"ticker": ticker}, limit=limit
            )
        ]


host = "database" if is_running_in_docker() else "localhost"
uri = f'mongodb://{get_secret("mongodb_username")}:{get_secret("mongodb_password")}@{host}'
storage = MongoDbStorage(uri)
