import datetime as dt
from abc import ABC, abstractmethod

from pymongo import MongoClient

from opa.app_secrets import get_secret
from opa.utils import is_running_in_docker


class Storage(ABC):
    @abstractmethod
    def insert_historical(self, historical: list[any]):
        ...

    @abstractmethod
    def get_historical(self, ticker: str, limit: int = 500):
        ...


class MongoDbStorage(Storage):
    def __init__(self, uri: str) -> None:
        client = MongoClient(uri)

        self.db = client.get_database("stock_market")
        self.collections = {
            coll: self.db.get_collection(coll) for coll in ["historical", "streaming"]
        }

    def insert_historical(self, historical: list[any]):
        self.collections["historical"].insert_many(
            [
                {
                    # MongoDB only handles datetimes and not dates
                    "date": dt.datetime.combine(v.date, dt.time.min),
                    "close": v.close,
                    "symbol": historical.symbol,
                }
                for v in historical.historical
            ]
        )

    def get_historical(self, ticker: str, limit: int = 500):
        return [
            {"date": d["date"], "close": d["close"]}
            for d in self.collections["historical"].find(
                {"symbol": ticker}, limit=limit
            )
        ]


host = "database" if is_running_in_docker() else "localhost"
uri = f'mongodb://{get_secret("mongodb_username")}:{get_secret("mongodb_password")}@{host}'
storage = MongoDbStorage(uri)
