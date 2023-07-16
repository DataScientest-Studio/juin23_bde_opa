import datetime as dt

from pymongo import MongoClient

from opa.app_secrets import get_secret
from opa.utils import is_running_in_docker


mongo_host = "database" if is_running_in_docker() else "localhost"
mongo_uri = f'mongodb://{get_secret("mongodb_username")}:{get_secret("mongodb_password")}@{mongo_host}'
mongo_client = MongoClient(mongo_uri)

opa_db = mongo_client.get_database("opa")
hist_collection = opa_db.get_collection("historical")


def insert_historical(historical: list[any]):
    hist_collection.insert_many(
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


def get_historical(ticker: str, limit: int = 500):
    return [
        {"date": d["date"], "close": d["close"]}
        for d in hist_collection.find({"symbol": ticker}, limit=limit)
    ]
