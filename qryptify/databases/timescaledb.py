import sys

from loguru import logger
import psycopg2
from psycopg2.extras import execute_values

from qryptify.config.config import TimescaleDBConfig
from qryptify.constants.timescale_constants import TimescaleDBTables


class TimescaleDB:

    def __init__(self,
                 connection_url=None,
                 database=None,
                 user=None,
                 password=None):
        try:
            self.connection_url = connection_url or TimescaleDBConfig.CONNECTION_URL
            self.database = database or TimescaleDBConfig.DATABASE
            self.user = user or TimescaleDBConfig.USER
            self.password = password or TimescaleDBConfig.PASSWORD
            # If connection_url looks like a DSN, use it directly
            if self.connection_url and self.connection_url.startswith(
                    "postgresql://"):
                self.conn = psycopg2.connect(self.connection_url)
                logger.info(
                    f"Connected to TimescaleDB using DSN: {self.connection_url}"
                )
            else:
                self.conn = psycopg2.connect(dbname=self.database,
                                             user=self.user,
                                             password=self.password,
                                             host=self.connection_url)
                logger.info(
                    f"Connected to TimescaleDB at {self.connection_url} with database {self.database}"
                )
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
        except Exception as e:
            logger.exception(
                f"Failed to connect to TimescaleDB: {self.connection_url}: {e}"
            )
            sys.exit(1)

    def get_latest_price(self, coin):
        query = f"SELECT price FROM {TimescaleDBTables.prices} WHERE coin = %s ORDER BY recv_time DESC LIMIT 1"
        self.cur.execute(query, (coin, ))
        row = self.cur.fetchone()
        return row[0] if row else None

    def insert_realtime_price(self, doc):
        query = f"""
        INSERT INTO {TimescaleDBTables.prices} (coin, price, event_time, trade_time, recv_time)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (coin, event_time) DO UPDATE SET price = EXCLUDED.price, trade_time = EXCLUDED.trade_time, recv_time = EXCLUDED.recv_time
        """
        self.cur.execute(query, (doc['coin'], doc['price'], doc['event_time'],
                                 doc['trade_time'], doc['recv_time']))

    def insert_realtime_candle(self, doc):
        query = f"""
        INSERT INTO {TimescaleDBTables.candlesticks} (timestamp, open, high, low, close, volume, close_time, quote_asset_volume, number_of_trades, taker_buy_base, taker_buy_quote, symbol, interval)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (timestamp, symbol, interval) DO UPDATE SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, close = EXCLUDED.close, volume = EXCLUDED.volume, close_time = EXCLUDED.close_time, quote_asset_volume = EXCLUDED.quote_asset_volume, number_of_trades = EXCLUDED.number_of_trades, taker_buy_base = EXCLUDED.taker_buy_base, taker_buy_quote = EXCLUDED.taker_buy_quote
        """
        self.cur.execute(
            query, (doc['timestamp'], doc['open'], doc['high'], doc['low'],
                    doc['close'], doc['volume'], doc['close_time'],
                    doc['quote_asset_volume'], doc['number_of_trades'],
                    doc['taker_buy_base'], doc['taker_buy_quote'],
                    doc['symbol'], doc['interval']))
