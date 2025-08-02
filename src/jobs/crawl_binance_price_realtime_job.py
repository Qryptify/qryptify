import json
import os
import time
import websocket
from src.databases.mongodb import MongoDB
from src.utils.file_utils import smart_open


class CrawlBinancePriceRealtimeJob:
    def __init__(self, item_exporter: MongoDB, coin, last_sync_file):
        self.item_exporter = item_exporter
        self.coin = coin.upper()
        self.last_sync_file = last_sync_file

    def read_last_sync_time(self):
        if not self.last_sync_file or not os.path.exists(self.last_sync_file):
            return 0
        with smart_open(self.last_sync_file, "r") as f:
            try:
                return float(f.read().strip())
            except:
                return 0

    def write_last_sync_time(self, timestamp: float):
        if self.last_sync_file:
            with smart_open(self.last_sync_file, "w") as f:
                f.write(str(timestamp))

    def on_message(self, ws, message):
        data = json.loads(message)
        price = float(data['p'])
        trade_time = data['T'] / 1000
        event_time = data['E'] / 1000
        now = time.time()

        last_sync = self.read_last_sync_time()

        if now - last_sync < 1.0:
            return

        doc = {
            'coin': self.coin,
            'price': price,
            'event_time': event_time,
            'trade_time': trade_time,
            'recv_time': int(now * 1000)
        }

        self.item_exporter.insert_realtime_price(doc)
        self.write_last_sync_time(now)

    def on_error(self, ws, error):
        print(f"[{self.coin}] ❌ WebSocket Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print(f"[{self.coin}] 🔌 WebSocket Closed")

    def on_open(self, ws):
        print(f"[{self.coin}] ✅ WebSocket Connected")

    def run(self):
        symbol = self.coin.lower()
        socket_url = f"wss://fstream.binance.com/ws/{symbol}usdt@trade"

        ws = websocket.WebSocketApp(
            socket_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        ws.run_forever()
