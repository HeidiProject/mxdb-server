# Wrapper around pymongo calls to handle autoreconect timeout to enable connection 
# retries when deployed with NGINX 

import app
from app import mongo
import pymongo
import time
import logging

logging.basicConfig(
    level=logging.WARN, format="%(asctime)s - %(name)s - %(levelname)s %(message)s"
)

MONGO_CONNECT_TIMEOUT = app.MONGO_CONNECT_TIMEOUT / 1000.0  # ms -> s
NGINX_UPSTREAM_SERVER_TIMEOUT = app.NGINX_UPSTREAM_SERVER_TIMEOUT


class MongoNotConnected(Exception):
    pass


def autoreconnect_to_mongo(mongo_op):
    """Handle reconnection retries to MongoDB server"""

    def wrapper(*arg, **kwargs):
        start = time.time()

        while (
            time.time() - start < NGINX_UPSTREAM_SERVER_TIMEOUT - MONGO_CONNECT_TIMEOUT
        ):  # try few times before Nginx/client timeouts.
            try:
                return mongo_op(*arg, **kwargs)
            except pymongo.errors.AutoReconnect:
                logging.warning(
                    "Cannot connect to mongo server - attempting to reconnect"
                )

        logging.warning("No success establishing connection to mongo server")
        raise MongoNotConnected("Connection to MongoDB server could not be established")

    return wrapper


@autoreconnect_to_mongo
def insert_one(collection, message):
    return mongo.db[collection].insert_one(message).inserted_id


@autoreconnect_to_mongo
def insert_many(collection, message):
    return mongo.db[collection].insert_many(message).inserted_ids


@autoreconnect_to_mongo
def replace_one(collection, query, message, upsert=False):
    return mongo.db[collection].replace_one(query, message, upsert=upsert)


@autoreconnect_to_mongo
def distinct(collection, key, query):
    return mongo.db[collection].distinct(key, query)


@autoreconnect_to_mongo
def find(collection, query, **kwargs):
    return mongo.db[collection].find(query, **kwargs)


@autoreconnect_to_mongo
def find_one(collection, query):
    return mongo.db[collection].find_one(query)


@autoreconnect_to_mongo
def aggregate(collection, query):
    return mongo.db[collection].aggregate(query)


@autoreconnect_to_mongo
def update_one(collection, query, update, upsert=False):
    return mongo.db[collection].update_one(query, {"$set": update}, upsert=upsert)

@autoreconnect_to_mongo
def update_many(collection, query, update, upsert=False):
    return mongo.db[collection].update_many(query, {"$set": update}, upsert=upsert)


@autoreconnect_to_mongo
def delete_one(collection, query):
    return mongo.db[collection].delete_one(query)


@autoreconnect_to_mongo
def delete_many(collection, query):
    return mongo.db[collection].delete_many(query)
