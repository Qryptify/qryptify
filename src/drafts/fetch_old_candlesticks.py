import requests
from pymongo import MongoClient
import time


class BinanceCandleFetcher:
    def __init__(self, symbol, interval='1m', limit=1000, mongo_uri='mongodb://localhost:27017/', db_name='binance', collection_name='candles'):
        self.symbol = symbol.upper()
        self.interval = interval
        self.limit = limit
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]

    def fetch_candlesticks(self):
        url = 'https://fapi.binance.com/fapi/v1/klines'
        params = {
            'symbol': self.symbol,
            'interval': self.interval,
            'limit': self.limit
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def save_to_mongo(self, candles):
        for candle in candles:
            kline = {
                "timestamp": int(candle[0]),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
                "close_time": int(candle[6]),
                "quote_asset_volume": float(candle[7]),
                "number_of_trades": int(candle[8]),
                "taker_buy_base": float(candle[9]),
                "taker_buy_quote": float(candle[10]),
                "ignore": candle[11],
                "symbol": self.symbol,
                "interval": self.interval
            }
            self.collection.update_one(
                {"timestamp": kline["timestamp"], "symbol": kline["symbol"]},
                {"$set": kline},
                upsert=True
            )

    def run(self):
        print(f"Fetching candlesticks for {self.symbol}")
        candles = self.fetch_candlesticks()
        self.save_to_mongo(candles)
        print(f"Saved {len(candles)} candles to MongoDB")


if __name__ == "__main__":
    fetcher = BinanceCandleFetcher(
        symbol="BTCUSDT",
        interval="1m",
        limit=500
    )
    fetcher.run()
