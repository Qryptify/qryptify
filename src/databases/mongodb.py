import sys

import pymongo

from config import MongoDBConfig
from pymongo import MongoClient

from src.constants.mongo_constants import MongoDBCollections
from src.utils.logger_utils import get_logger

logger = get_logger('MongoDB')


class MongoDB:
    def __init__(self, connection_url, database=MongoDBConfig.DATABASE):
        try:
            if not connection_url:
                connection_url = 'mongodb://localhost:27017/'
            self.connection = MongoClient(connection_url)
            self.mongo_db = self.connection[database]
            logger.info(f"Connected to {connection_url} with database {database}")
        except Exception as e:
            logger.exception(f"Failed to connect to MongoDB: {connection_url}: {e}")
            sys.exit(1)

        self._collectors_col = self.mongo_db[MongoDBCollections.collectors]
        self._prices_col = self.mongo_db[MongoDBCollections.prices]

    def get_latest_price(self, coin):
        filters = {
            'coin': coin,
        }
        doc = self._prices_col.find(filter=filters).sort(('recv_time', pymongo.DESCENDING)).limit(1)[0]
        return doc['price']

    def insert_realtime_price(self, doc):
        self._prices_col.insert_one(doc)

