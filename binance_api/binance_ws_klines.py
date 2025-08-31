"""
binance_ws_klines
Endpoint (combined streams): wss://fstream.binance.com/stream?streams=<symbol>@kline_<interval>/...
Docs: https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams

This example connects to Binance USDS-Margined Futures WebSocket combined
streams and prints CLOSED candlesticks (kline events where k["x"] == True),
matching the ingestor's WebSocket usage.
"""

import asyncio
from datetime import datetime
from datetime import timezone
import json

import websockets

WS_BASE = "wss://fstream.binance.com"
ENDPOINT = "/stream"

# Demo configuration (mirrors the style of other examples)
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVAL = "1m"
COUNT = 5  # how many CLOSED candles to print then exit

# Expected fields and their types on the combined stream event
EVENT_FIELDS = [("stream", str), ("data", dict)]

# Expected fields and types within the kline payload (data["k"]) used by ingestor
KLINE_FIELDS = [
    ("t", int),  # Open time (ms)
    ("T", int),  # Close time (ms)
    ("i", str),  # Interval
    ("o", str),  # Open
    ("h", str),  # High
    ("l", str),  # Low
    ("c", str),  # Close
    ("v", str),  # Volume (base)
    ("n", int),  # Number of trades
    ("x", bool),  # Is kline closed
    ("q", str),  # Quote asset volume
    ("V", str),  # Taker buy base asset volume
    ("Q", str),  # Taker buy quote asset volume
    ("B", str),  # Ignore
]


def _to_iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def _build_url(symbols, interval: str) -> str:
    streams = "/".join(f"{s.lower()}@kline_{interval}" for s in symbols)
    return f"{WS_BASE}{ENDPOINT}?streams={streams}"


async def _print_closed_klines(url: str, count: int) -> None:
    printed = 0
    async with websockets.connect(url, open_timeout=10) as ws:
        async for raw in ws:
            msg = json.loads(raw)
            # Basic envelope verification (combined streams)
            for name, dtype in EVENT_FIELDS:
                value = msg.get(name)
                assert isinstance(value, dtype), (
                    f"Type mismatch for '{name}': expected {dtype.__name__}, "
                    f"got {type(value).__name__}")

            data = msg["data"]
            k = data.get("k")
            sym = data.get("s")
            if not k or not sym:
                continue

            # Only proceed on CLOSED candles; verify fields on the first one
            if k.get("x") is True:
                if printed == 0:
                    print("\nClosed Kline (schema-verified):\n")
                    for key, dtype in KLINE_FIELDS:
                        val = k.get(key)
                        assert isinstance(val, dtype), (
                            f"Type mismatch for 'k.{key}': expected {dtype.__name__}, "
                            f"got {type(val).__name__}")
                        print(f"k.{key:<2} ({dtype.__name__}): {val}")

                print(
                    f"{sym} {k['i']} closed @ {_to_iso(k['T'])} "
                    f"O:{k['o']} H:{k['h']} L:{k['l']} C:{k['c']} V:{k['v']}")
                printed += 1
                if printed >= count:
                    break


if __name__ == "__main__":
    url = _build_url(SYMBOLS, INTERVAL)
    print("WebSocket URL:", url)
    print(f"Subscribing to: {', '.join(SYMBOLS)} @ {INTERVAL}")
    try:
        asyncio.run(_print_closed_klines(url, COUNT))
    except KeyboardInterrupt:
        print("Interrupted by user.")
"""
Output (example):
WebSocket URL: wss://fstream.binance.com/stream?streams=btcusdt@kline_1m/ethusdt@kline_1m
Subscribing to: BTCUSDT, ETHUSDT @ 1m

Closed Kline (schema-verified):
k.t  (int): 1754817420000
k.T  (int): 1754817479999
k.i  (str): 1m
k.o  (str): 118359.50
k.h  (str): 118359.50
k.l  (str): 118300.00
k.c  (str): 118300.00
k.v  (str): 93.114
k.n  (int): 1301
k.x  (bool): True
k.q  (str): 11017878.82960
k.V  (str): 6.442
k.Q  (str): 762140.16380
k.B  (str): 0

BTCUSDT 1m closed @ 2025-08-10T09:17:59+00:00 O:118359.50 H:118359.50 L:118300.00 C:118300.00 V:93.114
ETHUSDT 1m closed @ 2025-08-10T09:17:59+00:00 O:... H:... L:... C:... V:...
...
"""
