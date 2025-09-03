from __future__ import annotations

from loguru import logger
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from qryptify.data.timescale import AsyncTimescaleRepo
from qryptify.data.timescale import TimescaleRepo

from .backfill_runner import run_backfill
from .binance_client import BinanceClient
from .live_runner import run_live


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=8))
async def run_all(cfg: dict) -> None:
    """Orchestrate backfill then live phases with a shared repo and client."""
    client = BinanceClient(cfg["rest"]["endpoint"], cfg["ws"]["endpoint"])
    dsn = cfg["db"]["dsn"]

    _ = await client.server_time_ms()

    repo_sync = TimescaleRepo(dsn)
    repo_sync.connect()
    try:
        logger.info("Backfill phase starting")
        await run_backfill(cfg, repo_sync, client)
    finally:
        repo_sync.close()

    logger.info("Live phase starting")
    repo_async = AsyncTimescaleRepo(dsn)
    await repo_async.connect()
    try:
        await run_live(cfg, repo_async, client)
    finally:
        repo_async.close()
