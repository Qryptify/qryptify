from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator, List, Optional

import httpx
from loguru import logger
import websockets

KLINE_PATH = "/fapi/v1/klines"
TIME_PATH = "/fapi/v1/time"


class BinanceClient:
    """Minimal Binance Futures client for REST and WebSocket klines."""

    def __init__(self, rest_base: str, ws_base: str, timeout_s: float = 30.0):
        self._rest_base = rest_base.rstrip("/")
        self._ws_base = ws_base.rstrip("/")
        self._timeout_s = timeout_s

    async def server_time_ms(self) -> int:
        """Fetch server time in milliseconds since epoch (UTC)."""
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
        """Fetch candlestick arrays via REST for a symbol/interval window."""
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        if start_ms is not None:
            params["startTime"] = start_ms
        if end_ms is not None:
            params["endTime"] = end_ms
        async with httpx.AsyncClient(timeout=self._timeout_s) as cli:
            r = await cli.get(self._rest_base + KLINE_PATH, params=params)
            r.raise_for_status()
            return r.json()

    async def ws_kline_stream_pairs(
            self, pairs: list[tuple[str, str]]) -> AsyncGenerator[dict, None]:
        """
        Yields closed kline payloads as dicts for mixed (symbol, interval) pairs:
        {
          "symbol": "BTCUSDT",
          "k": { "t": open_time, "T": close_time, "i": "1m", "x": true, ... }
        }
        """
        streams = [f"{s.lower()}@kline_{i}" for s, i in pairs]
        async for item in self._ws_kline_stream_from_streams(streams):
            yield item

    async def _ws_kline_stream_from_streams(
            self, streams: list[str]) -> AsyncGenerator[dict, None]:
        streams_qs = "/".join(streams)
        url = f"{self._ws_base}?streams={streams_qs}"
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


async def _ws_reconnect(url: str,
                        initial_ms: int = 500,
                        max_ms: int = 8000,
                        *,
                        jitter: bool = False):
    """Reconnect loop with optional jittered exponential backoff.

    Behavior is unchanged by default (no jitter). When jitter=True, a random
    +/- 20% jitter is applied to the sleep duration to avoid thundering herd.
    """
    backoff = initial_ms
    while True:
        try:
            async with websockets.connect(url, open_timeout=10) as ws:
                yield ws
                backoff = initial_ms  # reset after a clean session
        except Exception:
            delay = backoff
            if jitter:
                try:
                    import random

                    # +/- 20% jitter
                    jitter_mult = 1.0 + random.uniform(-0.2, 0.2)
                    delay = int(max(1, delay * jitter_mult))
                except Exception:
                    pass
            logger.warning(f"WebSocket connect error; retry in {delay} ms")
            await asyncio.sleep(delay / 1000)
            backoff = min(backoff * 2, max_ms)
            continue
