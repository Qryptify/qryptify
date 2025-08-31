from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple

import httpx
from loguru import logger
import websockets

KLINE_PATH = "/fapi/v1/klines"
TIME_PATH = "/fapi/v1/time"


class BinanceClient:

    def __init__(self, rest_base: str, ws_base: str, timeout_s: float = 30.0):
        self._rest_base = rest_base.rstrip("/")
        self._ws_base = ws_base.rstrip("/")
        self._timeout_s = timeout_s

    async def server_time_ms(self) -> int:
        async with httpx.AsyncClient(timeout=self._timeout_s) as cli:
            r = await cli.get(self._rest_base + TIME_PATH)
            r.raise_for_status()
            return int(r.json()["serverTime"])

    async def klines(
        self,
        symbol: str,
        interval: str,
        start_ms: Optional[int] = None,
        end_ms: Optional[int] = None,
        limit: int = 1500,
    ) -> List[list]:
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_ms is not None: params["startTime"] = start_ms
        if end_ms is not None: params["endTime"] = end_ms
        async with httpx.AsyncClient(timeout=self._timeout_s) as cli:
            r = await cli.get(self._rest_base + KLINE_PATH, params=params)
            r.raise_for_status()
            return r.json()

    async def ws_kline_stream(self, symbols: list[str], interval: str):
        """
        Yields closed kline payloads as dicts:
        {
          "s": "BTCUSDT",
          "k": { "t": open_time, "T": close_time, "i": "1m", "x": true, ... }
        }
        """
        streams = "/".join(f"{s.lower()}@kline_{interval}" for s in symbols)
        url = f"{self._ws_base}?streams={streams}"
        async for ws in _ws_reconnect(url):
            try:
                logger.info(f"WebSocket connected: {url}")
                async for msg in ws:
                    data = json.loads(msg)
                    k = data.get("data", {}).get("k")
                    if k and k.get("x") is True:
                        yield {"symbol": data["data"]["s"], "k": k}
            except websockets.ConnectionClosed:
                logger.warning("WebSocket connection closed; reconnecting…")
                continue


async def _ws_reconnect(url: str, initial_ms: int = 500, max_ms: int = 8000):
    backoff = initial_ms
    while True:
        try:
            async with websockets.connect(url, open_timeout=10) as ws:
                yield ws
                backoff = initial_ms  # reset after a clean session
        except Exception:
            logger.warning(f"WebSocket connect error; retry in {backoff} ms")
            await asyncio.sleep(backoff / 1000)
            backoff = min(backoff * 2, max_ms)
            continue
