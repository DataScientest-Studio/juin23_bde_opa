from pymongo import MongoClient
from pymongo.errors import BulkWriteError

from opa.core import environment
from opa.core.financial_data import StockValue, StockValueType
from opa.core.storage import Storage


class MongoDbStorage(Storage):
    def __init__(self, uri: str) -> None:
        client: MongoClient = MongoClient(uri, serverSelectionTimeoutMS=5000)

        self.db = client.get_database("stock_market")
        self.collections = {
            coll: self.db.get_collection(coll.value) for coll in StockValueType
        }

    def insert_values(self, values: list[StockValue], type_: StockValueType):
        collection = self.collections[type_]
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
        collection = self.collections[type_]

        return [
            StockValue(**d) for d in collection.find({"ticker": ticker}, limit=limit)
        ]

    def get_all_tickers(self) -> list[str]:
        # We first build a set to ensure that all values stay distinct and
        # then convert it to a list in order to be indexable
        return list(
            {
                t
                for collection in self.collections.values()
                for t in collection.distinct("ticker")
            }
        )


storage = MongoDbStorage(environment.mongodb_uri)
