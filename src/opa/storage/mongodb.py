from collections import Counter

from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from loguru import logger

from opa.core.financial_data import (
    StockValue,
    StockValueType,
    CompanyInfo,
    StockCollectionStats,
)
from opa.core.storage import Storage


# MongoDB error codes that we handle here
# https://github.com/mongodb/mongo/blob/master/src/mongo/base/error_codes.yml
MULTIPLE_ERRORS_OCCURRED_ERROR = 65
DUPLICATE_KEY_ERROR = 11000
DOCUMENT_VALIDATION_FAILURE_ERROR = 121


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
            # BulkWriteError has a structure that is not very well documented either in
            # pymongo or in MongoDB documentation :
            #   * an error code `code`
            #   * details about the errors in `details`
            #
            # `err.details`` is a dictionary with the following keys :
            #
            # ```
            # dict_keys([
            #    'writeErrors', 'writeConcernErrors', 'nInserted', 'nUpserted', 'nMatched', 'nModified', 'nRemoved', 'upserted'
            # ])
            # ```
            #
            # `err.details["writeErrors"]` is a [verbose] list of ALL the errors.
            #
            # Errors have the following structure :
            # {'index': * the index of the document that failed validation within the stream we sent * ,
            #  'code': * the error code *,
            #  'errmsg': * a nice error message *,
            #  'op': * the document we tried to insert, as a dict *}
            #
            # Duplication errors have the following additional fields :
            # {'keyPattern': * the fields that are duplicated, as a dict *,
            #  'keyValue': * the value of the fields that are duplicates, as a dict *}
            #
            # Validation errors have the following additional fields :
            # {'errInfo': * a dictionary with additional details *}
            # The errInfo["details"] dictionary has the keys "operatorName", "title", "schemaRulesNotSatisfied".
            if err.code != MULTIPLE_ERRORS_OCCURRED_ERROR:
                raise err

            write_errors = err.details["writeErrors"]

            nb_inserted = err.details["nInserted"]
            code_counter = Counter((e["code"] for e in write_errors))
            duplicate_counter = Counter(
                (
                    frozenset(e["keyPattern"].keys())
                    for e in write_errors
                    if e["code"] == DUPLICATE_KEY_ERROR
                )
            )

            logger.warning(
                "Only {nb_inserted} stock values out of {write_operations} could be inserted "
                "({nb_expected_duplicates} were duplicates of existing values)",
                nb_inserted=nb_inserted,
                write_operations=len(insertable),
                nb_expected_duplicates=duplicate_counter[frozenset(["ticker", "date"])],
            )

            unexpected_duplicates = (
                code_counter[DUPLICATE_KEY_ERROR]
                - duplicate_counter[frozenset(["ticker", "date"])]
            )
            if unexpected_duplicates:
                logger.error(
                    "{} values were unexpected duplicates", unexpected_duplicates
                )

            validation_errors = code_counter[DOCUMENT_VALIDATION_FAILURE_ERROR]
            if validation_errors:
                logger.error("{} documents had validation errors", validation_errors)

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

    def get_stats(self, type_: StockValueType) -> dict[str, StockCollectionStats]:
        ret = {
            grouped["_id"]: StockCollectionStats(
                **{k: v for k, v in grouped.items() if k != "_id"}
            )
            for grouped in self.collections[type_].aggregate(
                [
                    {
                        "$group": {
                            "_id": "$ticker",
                            "latest": {"$max": "$date"},
                            "oldest": {"$min": "$date"},
                            "count": {"$count": {}},
                        }
                    }
                ]
            )
        }
        logger.info("Getting stats from storage")

        return ret
