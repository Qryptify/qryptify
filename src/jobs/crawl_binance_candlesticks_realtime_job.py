import requests
import time

from cli_scheduler import SchedulerJob
from src.databases.mongodb import MongoDB
from src.utils.logger_utils import get_logger
from src.utils.file_utils import init_last_synced_file, read_last_synced_file, write_last_synced_time

logger = get_logger('Crawl Binance Candlesticks Realtime Job')


class CrawlBinanceCandlesticksRealtimeJob(SchedulerJob):
    def __init__(self, item_exporter: MongoDB, coin: str, candle_interval: str, scheduler=None, last_sync_file=None):
        super().__init__(scheduler=scheduler)

        self.item_exporter = item_exporter
        self.coin = coin.upper()
        self.last_sync_file = last_sync_file
        self.candle_interval = candle_interval
        init_last_synced_file(0, self.last_sync_file)

    def _fetch_candles(self, start_time_s):
        url = 'https://fapi.binance.com/fapi/v1/klines'
        params = {
            'symbol': self.coin,
            'interval': self.candle_interval,
            'startTime': start_time_s * 1000,
            'limit': 15
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch candles: {e}")
            return []

    def _execute(self, *args, **kwargs):
        last_sync_s = read_last_synced_file(self.last_sync_file)
        now_s = int(time.time())

        candles = self._fetch_candles(last_sync_s)

        if not candles:
            logger.info("No new candles.")
            return

        count = 0
        for candle in candles:
            timestamp_s = int(candle[0] // 1000)
            if timestamp_s <= last_sync_s:
                continue

            kline = {
                "timestamp": timestamp_s,
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
                "symbol": self.coin,
                "interval": self.candle_interval
            }

            self.item_exporter.insert_realtime_candle(kline)
            last_sync_s = max(last_sync_s, timestamp_s)
            count += 1

        write_last_synced_time(last_sync_s, self.last_sync_file)
        logger.info(f"Saved {count} new candles for {self.coin} at interval {self.candle_interval}")
