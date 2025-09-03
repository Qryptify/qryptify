"""Backfill utilities and runner.

Backfills historical klines for configured pairs using Binance REST, writing
idempotently into TimescaleDB and advancing the resume pointer per pair.
"""
from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Dict

from loguru import logger

from qryptify.shared.intervals import step_of
from qryptify.shared.pairs import symbol_interval_pairs_from_cfg
from qryptify.shared.time import to_dt
from qryptify.shared.time import to_ms


def _parse_kline(symbol: str, interval: str, arr: list) -> Dict:
    """Parse a REST kline array into a DB row dict.

    Binance kline schema indices:
    0 open time(ms), 1 open, 2 high, 3 low, 4 close, 5 volume,
    6 close time(ms), 7 quote asset vol, 8 trades, 9 taker buy base,
    10 taker buy quote, 11 ignore
    """
    return {
        "ts": to_dt(arr[0]),
        "symbol": symbol,
        "interval": interval,
        "open": float(arr[1]),
        "high": float(arr[2]),
        "low": float(arr[3]),
        "close": float(arr[4]),
        "volume": float(arr[5]),
        "close_time": to_dt(arr[6]),
        "quote_asset_volume": float(arr[7]),
        "number_of_trades": int(arr[8]),
        "taker_buy_base": float(arr[9]),
        "taker_buy_quote": float(arr[10]),
    }


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
