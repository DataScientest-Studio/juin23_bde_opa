import os

from opa import environment

from .mongodb import MongoDbStorage


if environment.in_docker:
    mongodb_host = "database"
else:
    mongodb_host = "localhost"

mongodb_uri = "mongodb://{username}:{password}@{host}".format(
    username=environment.get_secret("mongodb_username"),
    password=environment.get_secret("mongodb_password"),
    host=mongodb_host,
)

opa_storage = MongoDbStorage(
    mongodb_uri, os.getenv("MONGO_DATABASE", "stock_market-dev")
)
