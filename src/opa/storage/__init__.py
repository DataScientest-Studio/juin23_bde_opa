import os

from opa import settings

from .mongodb import MongoDbStorage


mongodb_uri = "mongodb://{username}:{password}@{host}".format(
    username=settings.secrets.mongodb_username,
    password=settings.secrets.mongodb_password,
    host=settings.mongo_host,
)

opa_storage = MongoDbStorage(mongodb_uri, settings.mongo_database)
