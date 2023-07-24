import datetime as dt
from abc import ABC, abstractmethod
from typing import Any

from pymongo import MongoClient
from pymongo.errors import BulkWriteError

from opa.app_secrets import get_secret
from opa.utils import is_running_in_docker
from opa.financial_data import StockValue, StockValueType


class Storage(ABC):
    @abstractmethod
    def insert_values(self, values: list[StockValue], type_: StockValueType):
        ...

    @abstractmethod
    def get_values(
        self, ticker: str, type_: StockValueType, limit: int = 500
    ) -> list[StockValue]:
        ...

    @abstractmethod
    def get_all_tickers(self) -> list[str]:
        ...


class MongoDbStorage(Storage):
    def __init__(self, uri: str) -> None:
        client: MongoClient = MongoClient(uri, serverSelectionTimeoutMS=5000)

        self.db = client.get_database("stock_market")
        self.collections = {
            coll: self.db.get_collection(coll) for coll in ["historical", "streaming"]
        }

    def insert_values(self, values: list[StockValue], type_: StockValueType):
        collection = self.collections[type_.value]
        insertable = [
            {k: v for (k, v) in val.__dict__.items() if v is not None} for val in values
        ]
        try:
            # `ordered=False` ensures that at least some data will be inserted even if there are errors
            return collection.insert_many(insertable, ordered=False)
        except BulkWriteError as err:
            error_codes = {e["code"] for e in err.details["writeErrors"]}

            if error_codes == set([121]):
                print("ERROR: all records failed validation")

    def get_values(
        self, ticker: str, type_: StockValueType, limit: int = 500
    ) -> list[StockValue]:
        collection = self.collections[type_.value]

        return [
            StockValue(**d) for d in collection.find({"ticker": ticker}, limit=limit)
        ]

    def get_all_tickers(self) -> list[str]:
        return self.collections["historical"].distinct("ticker")


host = "database" if is_running_in_docker() else "localhost"
uri = f'mongodb://{get_secret("mongodb_username")}:{get_secret("mongodb_password")}@{host}'
storage = MongoDbStorage(uri)
