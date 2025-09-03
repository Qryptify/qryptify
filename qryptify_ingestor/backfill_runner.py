"""Backfill utilities and runner.

Backfills historical klines for configured pairs using Binance REST, writing
idempotently into TimescaleDB and advancing the resume pointer per pair.
"""
from __future__ import annotations

from datetime import datetime
from datetime import timezone

from loguru import logger

from qryptify.ingestor.parsers import parse_rest_kline_row
from qryptify.ingestor.types import KlineRow
from qryptify.shared.intervals import step_of
from qryptify.shared.pairs import symbol_interval_pairs_from_cfg
from qryptify.shared.time import to_dt
from qryptify.shared.time import to_ms


def _parse_kline(symbol: str, interval: str, arr: list) -> KlineRow:
    """Wrapper kept for compatibility; delegates to shared parser."""
    return parse_rest_kline_row(symbol, interval, arr)


async def run_backfill(cfg: dict, repo, client) -> None:
    """Backfill historical klines per configured (symbol, interval) pair.

    - Resumes from `sync_state.last_closed_ts` when present, otherwise uses
      `backfill.start_date` from the config.
    - Writes with ON CONFLICT DO NOTHING to remain idempotent.
    """
    pairs = symbol_interval_pairs_from_cfg(cfg)
    page_limit = cfg["rest"]["klines_limit"]
    min_start = datetime.fromisoformat(cfg["backfill"]["start_date"].replace(
        "Z", "+00:00"))

    for symbol, interval in pairs:
        last = repo.get_last_closed_ts(symbol, interval)
        start_dt = max_dt(min_start, (last + step_of(interval)) if last else min_start)
        start_ms = to_ms(start_dt)
        logger.info(
            f"Backfill {symbol}/{interval} from {start_dt.isoformat()} (limit={page_limit})"
        )

        while True:
            batch = await client.klines(symbol,
                                        interval,
                                        start_ms=start_ms,
                                        limit=page_limit)
            if not batch:
                logger.info(f"Backfill {symbol}/{interval} complete (no more data)")
                break
            rows = [_parse_kline(symbol, interval, arr) for arr in batch]
            inserted = repo.upsert_klines(rows)
            # advance by last close
            last_close_ms = batch[-1][6]
            last_close_dt = to_dt(last_close_ms)
            repo.set_last_closed_ts(symbol, interval, last_close_dt)
            logger.info(
                f"Backfill {symbol}/{interval}: inserted={inserted} last_close={last_close_dt.isoformat()}"
            )

            # Stop when close to "now" (let live mode take over)
            if (datetime.now(timezone.utc) - last_close_dt) < step_of(interval):
                logger.info(
                    f"Backfill {symbol}/{interval} up-to-date through {last_close_dt.isoformat()}"
                )
                break
            start_ms = last_close_ms + 1


def max_dt(a: datetime, b: datetime) -> datetime:
    """Return the maximum of two datetimes."""
    return a if a >= b else b
