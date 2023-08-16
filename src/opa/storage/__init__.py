import os

from opa import settings

from .mongodb import MongoDbStorage


mongodb_uri = "mongodb://{username}:{password}@{host}:{port}".format(
    username=settings.secrets.mongodb_username,
    password=settings.secrets.mongodb_password,
    host=settings.mongo_host,
    port=settings.mongo_port,
)

opa_storage = MongoDbStorage(mongodb_uri, settings.mongo_database)
