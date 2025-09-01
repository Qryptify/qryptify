from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Dict

from loguru import logger

from .config_utils import symbol_interval_pairs_from_cfg


def _to_dt(ms: int) -> datetime:
    """Convert Binance millisecond epoch to timezone-aware UTC datetime."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def _to_ms(dt: datetime) -> int:
    """Convert timezone-aware datetime to millisecond epoch (UTC)."""
    return int(dt.timestamp() * 1000)


def _parse_kline(symbol: str, interval: str, arr: list) -> Dict:
    """Parse a REST kline array into a DB row dict.

    Binance kline schema indices:
    0 open time(ms), 1 open, 2 high, 3 low, 4 close, 5 volume,
    6 close time(ms), 7 quote asset vol, 8 trades, 9 taker buy base,
    10 taker buy quote, 11 ignore
    """
    return {
        "ts": _to_dt(arr[0]),
        "symbol": symbol,
        "interval": interval,
        "open": float(arr[1]),
        "high": float(arr[2]),
        "low": float(arr[3]),
        "close": float(arr[4]),
        "volume": float(arr[5]),
        "close_time": _to_dt(arr[6]),
        "quote_asset_volume": float(arr[7]),
        "number_of_trades": int(arr[8]),
        "taker_buy_base": float(arr[9]),
        "taker_buy_quote": float(arr[10]),
    }


async def run_backfill(cfg: dict, repo, client):
    """Backfill historical klines per configured (symbol, interval) pairs.

    For each pair, resumes from `sync_state.last_closed_ts` if present,
    otherwise from the configured `backfill.start_date`.
    """
    pairs = symbol_interval_pairs_from_cfg(cfg)
    limit = cfg["rest"]["klines_limit"]
    min_start = datetime.fromisoformat(cfg["backfill"]["start_date"].replace(
        "Z", "+00:00"))

    for sym, itv in pairs:
        last = repo.get_last_closed_ts(sym, itv)
        start_dt = max_dt(min_start,
                          (last + step_of(itv)) if last else min_start)
        start_ms = _to_ms(start_dt)
        logger.info(
            f"Backfill {sym}/{itv} from {start_dt.isoformat()} (limit={limit})"
        )

        while True:
            batch = await client.klines(sym,
                                        itv,
                                        start_ms=start_ms,
                                        limit=limit)
            if not batch:
                logger.info(f"Backfill {sym}/{itv} complete (no more data)")
                break
            rows = [_parse_kline(sym, itv, arr) for arr in batch]
            inserted = repo.upsert_klines(rows)
            # advance by last close
            last_close_ms = batch[-1][6]
            repo.set_last_closed_ts(sym, itv, _to_dt(last_close_ms))
            logger.info(
                f"Backfill {sym}/{itv}: inserted={inserted} last_close={_to_dt(last_close_ms).isoformat()}"
            )

            # Stop when close to "now" (let live mode take over)
            if (datetime.now(timezone.utc) -
                    _to_dt(last_close_ms)) < step_of(itv):
                logger.info(
                    f"Backfill {sym}/{itv} up-to-date through {_to_dt(last_close_ms).isoformat()}"
                )
                break
            start_ms = last_close_ms + 1


def max_dt(a: datetime, b: datetime) -> datetime:
    return a if a >= b else b


def step_of(interval: str) -> timedelta:
    table = {
        "1m": timedelta(minutes=1),
        "3m": timedelta(minutes=3),
        "5m": timedelta(minutes=5),
        "15m": timedelta(minutes=15),
        "30m": timedelta(minutes=30),
        "1h": timedelta(hours=1),
        "2h": timedelta(hours=2),
        "4h": timedelta(hours=4),
    }
    return table[interval]
