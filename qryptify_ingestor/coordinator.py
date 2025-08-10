from __future__ import annotations

import asyncio

from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from .backfill_runner import run_backfill
from .binance_client import BinanceClient
from .live_runner import run_live
from .timescale_repo import TimescaleRepo


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=8))
async def run_all(cfg):
    client = BinanceClient(cfg["rest"]["endpoint"], cfg["ws"]["endpoint"])
    repo = TimescaleRepo(cfg["db"]["dsn"])
    repo.connect()
    try:
        # Optional: check server clock skew
        _ = await client.server_time_ms()
        # Backfill first
        await run_backfill(cfg, repo, client)
        # Then live streaming until killed
        await run_live(cfg, repo, client)
    finally:
        repo.close()
