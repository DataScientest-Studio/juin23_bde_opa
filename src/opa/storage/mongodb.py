from collections import Counter

from pymongo import MongoClient
from pymongo.errors import BulkWriteError, CollectionInvalid
from loguru import logger

from opa.core.financial_data import (
    StockValue,
    StockValueKind,
    CompanyInfo,
    StockCollectionStats,
)
from opa.core.storage import Storage


# MongoDB error codes that we handle here
# https://github.com/mongodb/mongo/blob/master/src/mongo/base/error_codes.yml
MULTIPLE_ERRORS_OCCURRED_ERROR = 65
DUPLICATE_KEY_ERROR = 11000
DOCUMENT_VALIDATION_FAILURE_ERROR = 121


def _get_json_schema_validator(
    title: str, required_fields: list[str], field_types: dict[str, str]
) -> dict:
    props = {
        field: {"bsonType": type_, "description": f"'{field}' must be a {type_}"}
        for (field, type_) in field_types.items()
    }

    return {
        "$jsonSchema": {
            "bsonType": "object",
            "title": title,
            "required": required_fields,
            "properties": props,
            "additionalProperties": False,
        }
    }


class MongoDbStorage(Storage):
    stock_value_fields_types = {
        "_id": "objectId",
        "date": "date",
        "ticker": "string",
        "interval": "int",
        "close": "double",
        "open": "double",
        "low": "double",
        "high": "double",
        "volume": "int",
    }
    stock_value_required_fields = ["_id", "date", "close", "ticker", "interval"]
    date_ticker_unique_index = {"date": 1, "ticker": 1}

    collection_args = {
        StockValue: {
            "name": "stock_values",
            "create_args": {
                "validator": _get_json_schema_validator(
                    "Stock values validation",
                    stock_value_required_fields,
                    stock_value_fields_types,
                )
            },
            "unique_index": date_ticker_unique_index,
        },
        CompanyInfo: {"name": "company_info", "unique_index": {"symbol": 1}},
    }

    def __init__(self, uri: str, database: str) -> None:
        client: MongoClient = MongoClient(uri, serverSelectionTimeoutMS=5000)

        self.db = client.get_database(database)
        self._create_collections_if_not_exist()

        self.collections = {
            key: self.db.get_collection(coll["name"])
            for (key, coll) in self.collection_args.items()
        }

    def insert_values(self, values: list[StockValue]):
        collection = self.collections[StockValue]
        insertable = [
            {k: v for (k, v) in val.__dict__.items() if v is not None} for val in values
        ]
        try:
            # `ordered=False` ensures that at least some data will be inserted even if there are errors
            ret = collection.insert_many(insertable, ordered=False)
            logger.info(
                "Successfully inserted {count} new stock values",
                count=len(ret.inserted_ids),
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
        self, ticker: str, kind: StockValueKind, limit: int = 500
    ) -> list[StockValue]:
        collection = self.collections[StockValue]
        base_query = (
            {"open": {"$exists": 1}}
            if kind == StockValueKind.OHLC
            else {"open": {"$exists": 0}}
        )
        query = base_query | {"ticker": ticker}

        ret = [
            StockValue(**d)
            for d in collection.find(query, limit=limit).sort("date", -1)
        ]
        logger.info(
            "{count} {kind} stock values retrieved from storage",
            count=len(ret),
            kind=kind.value,
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

    def get_stats(self, kind: StockValueKind) -> dict[str, StockCollectionStats]:
        filter = (
            {"open": {"$exists": 1}}
            if kind == StockValueKind.OHLC
            else {"open": {"$exists": 0}}
        )
        ret = {
            grouped["_id"]: StockCollectionStats(
                **{k: v for k, v in grouped.items() if k != "_id"}
            )
            for grouped in self.collections[StockValue].aggregate(
                [
                    {"$match": filter},
                    {
                        "$group": {
                            "_id": "$ticker",
                            "latest": {"$max": "$date"},
                            "oldest": {"$min": "$date"},
                            "count": {"$count": {}},
                        }
                    },
                ]
            )
        }
        logger.info("Getting stats from storage")

        return ret

    def _create_collections_if_not_exist(self):
        for coll in self.collection_args.values():
            name = coll["name"]

            try:
                create_args = coll.get("create_args", {})
                self.db.create_collection(name, check_exists=True, **create_args)
                logger.info("Collection {} successfully created", name)

            except CollectionInvalid as err:
                msg = err.args[0]
                if "already exists" in msg:
                    # This is not an actual error
                    logger.info("Collection {} already exists, skipping creation", name)
                else:
                    raise err

            unique_index = coll.get("unique_index")
            if unique_index:
                # create_index is invariant and won't raise if the index already exists
                self.db[name].create_index(unique_index.items(), unique=True)
