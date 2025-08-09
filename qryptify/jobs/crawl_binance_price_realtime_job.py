import json
import os
import time

from loguru import logger
import websocket

from qryptify.databases.timescaledb import TimescaleDB
from qryptify.utils.file_utils import read_last_synced_file
from qryptify.utils.file_utils import write_last_synced_time


class CrawlBinancePriceRealtimeJob:

    def __init__(self, item_exporter: TimescaleDB, coin, last_sync_file):
        self.item_exporter = item_exporter
        self.coin = coin.upper()
        self.last_sync_file = last_sync_file
        init_last_synced_file(0, self.last_sync_file)

    def on_message(self, ws, message):
        data = json.loads(message)
        price = float(data['p'])
        trade_time = int(data['T'] / 1000)
        event_time = int(data['E'] / 1000)
        now = time.time()

        last_sync = read_last_synced_file(self.last_sync_file)

        if now - last_sync < 1.0:
            return

        doc = {
            'coin': self.coin,
            'price': price,
            'event_time': event_time,
            'trade_time': trade_time,
            'recv_time': now
        }

        self.item_exporter.insert_realtime_price(doc)
        write_last_synced_time(self.last_sync_file, now)

    def on_error(self, ws, error):
        print(f"[{self.coin}] ❌ WebSocket Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print(f"[{self.coin}] 🔌 WebSocket Closed")

    def on_open(self, ws):
        print(f"[{self.coin}] ✅ WebSocket Connected")

    def run(self):
        symbol = self.coin.lower()
        socket_url = f"wss://fstream.binance.com/ws/{symbol}usdt@trade"

        ws = websocket.WebSocketApp(socket_url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)

        ws.run_forever()
