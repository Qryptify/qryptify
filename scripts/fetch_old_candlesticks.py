import time

import requests
from src.databases.timescaledb import TimescaleDB


class BinanceCandleFetcher:

    def __init__(self, symbol, interval='1m', limit=1000):
        self.symbol = symbol.upper()
        self.interval = interval
        self.limit = limit
        self.db = TimescaleDB()

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

    def save_to_timescaledb(self, candles):
        for candle in candles:
            kline = {
                "timestamp": int(candle[0] // 1000),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
                "close_time": int(candle[6] // 1000),
                "quote_asset_volume": float(candle[7]),
                "number_of_trades": int(candle[8]),
                "taker_buy_base": float(candle[9]),
                "taker_buy_quote": float(candle[10]),
                "symbol": self.symbol,
                "interval": self.interval
            }
            self.db.insert_realtime_candle(kline)

    def run(self):
        print(f"Fetching candlesticks for {self.symbol}")
        candles = self.fetch_candlesticks()
        self.save_to_timescaledb(candles)
        print(f"Saved {len(candles)} candles to TimescaleDB")
