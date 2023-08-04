from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from loguru import logger

from opa.core.financial_data import StockValue, StockValueType, CompanyInfo
from opa.core.storage import Storage


class MongoDbStorage(Storage):
    def __init__(self, uri: str) -> None:
        client: MongoClient = MongoClient(uri, serverSelectionTimeoutMS=5000)

        self.db = client.get_database("stock_market")
        collections = {
            stock_type: stock_type.value for stock_type in StockValueType
        } | {CompanyInfo: "company_info"}
        self.collections = {
            key: self.db.get_collection(mongo_name)
            for (key, mongo_name) in collections.items()
        }

    def insert_values(self, values: list[StockValue], type_: StockValueType):
        collection = self.collections[type_]
        insertable = [
            {k: v for (k, v) in val.__dict__.items() if v is not None} for val in values
        ]
        try:
            # `ordered=False` ensures that at least some data will be inserted even if there are errors
            ret = collection.insert_many(insertable, ordered=False)
            logger.info(
                "Successfully inserted {count} new {type_} stock values",
                count=len(ret.inserted_ids),
                type_=type_.value,
            )

            return ret
        except BulkWriteError as err:
            error_codes = {e["code"] for e in err.details["writeErrors"]}
            write_errors = err.details["writeErrors"]
            error_codes = {e["code"] for e in write_errors}
            duplicate_keys = {
                frozenset(e["keyPattern"].keys())
                for e in write_errors
                if e["code"] == 11000
            }

            if error_codes < {121, 11000} and duplicate_keys == {
                frozenset(["ticker", "date"])
            }:
                logger.warning(
                    "All the new stock values failed validation or were duplicates"
                )

    def get_values(
        self, ticker: str, type_: StockValueType, limit: int = 500
    ) -> list[StockValue]:
        collection = self.collections[type_]

        ret = [
            StockValue(**d)
            for d in collection.find({"ticker": ticker}, limit=limit).sort("date", -1)
        ]
        logger.info(
            "{count} {type_} stock values retrieved from storage",
            count=len(ret),
            type_=type_.value,
        )

        return ret

    def get_all_tickers(self) -> list[str]:
        return self.collections[CompanyInfo].distinct("symbol")

    def insert_company_infos(self, infos: list[CompanyInfo]):
        try:
            return self.collections[CompanyInfo].insert_many(
                [i.model_dump() for i in infos], ordered=False
            )
        except BulkWriteError as err:
            logger.info(
                "Company infos were already present, ditching data from {} companies",
                len(infos),
            )

    def get_company_infos(self, tickers: list[str]) -> dict[str, CompanyInfo]:
        ret = {
            i["symbol"]: CompanyInfo(**i)
            for i in self.collections[CompanyInfo].find({"symbol": {"$in": tickers}})
        }
        logger.info("Fetched company info for {} companies from storage", len(ret))

        return ret
