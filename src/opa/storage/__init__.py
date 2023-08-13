import os

from opa import environment

from .mongodb import MongoDbStorage


mongodb_host = os.getenv("OPA_MONGO_HOST", "localhost")

mongodb_uri = "mongodb://{username}:{password}@{host}".format(
    username=environment.get_secret("mongodb_username"),
    password=environment.get_secret("mongodb_password"),
    host=mongodb_host,
)

opa_storage = MongoDbStorage(
    mongodb_uri, os.getenv("OPA_MONGO_DATABASE", "stock_market-dev")
)
