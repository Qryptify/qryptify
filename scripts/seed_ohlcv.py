"""
Seed minimal OHLCV data into the TimescaleDB used by this repo.

Usage:
  python scripts/seed_ohlcv.py --pair BTCUSDT/1h --rows 500

Notes:
  - DSN is read from qryptify_ingestor/config.yaml unless --dsn is provided.
  - Generates a simple price series with slight trend and noise.
  - Idempotent via repo.upsert_klines(); safe to run multiple times.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from datetime import timezone
import math
import random
from typing import List

import yaml

from qryptify.data.timescale import TimescaleRepo
from qryptify.shared.intervals import step_of
from qryptify.shared.pairs import parse_pair


def _default_dsn() -> str:
    with open("qryptify_ingestor/config.yaml", "r") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg["db"]["dsn"]


def _gen_rows(symbol: str, interval: str, rows: int) -> List[dict]:
    now = datetime.now(timezone.utc)
    # Choose step by interval string
    try:
        step = step_of(interval)
    except Exception as e:
        raise SystemExit(f"Unsupported interval for seed: {interval}") from e

    # Start some time ago so bars are in the past
    start = now - step * (rows + 5)
    base = 100.0
    trend = 0.01  # small upward trend per bar
    out = []
    last_close = base
    for i in range(rows):
        ts = start + step * i
        # Sine + noise around last close with light trend
        noise = random.uniform(-0.05, 0.05)
        delta = math.sin(i / 25.0) * 0.1 + trend + noise
        open_p = last_close
        close_p = max(open_p + delta, 0.01)
        high_p = max(open_p, close_p) + random.uniform(0.02, 0.12)
        low_p = min(open_p, close_p) - random.uniform(0.02, 0.12)
        vol = 1.0 + random.uniform(0, 0.5)
        row = {
            "ts": ts,
            "symbol": symbol,
            "interval": interval,
            "open": float(open_p),
            "high": float(high_p),
            "low": float(low_p),
            "close": float(close_p),
            "volume": float(vol),
            "close_time": ts + step,
            "quote_asset_volume": float(vol * (open_p + close_p) / 2.0),
            "number_of_trades": int(10 + i % 5),
            "taker_buy_base": float(vol * 0.4),
            "taker_buy_quote": float(vol * 0.4 * (open_p + close_p) / 2.0),
        }
        out.append(row)
        last_close = close_p
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Seed minimal OHLCV into TimescaleDB")
    ap.add_argument("--pair", required=True, help="SYMBOL/interval (e.g., BTCUSDT/1h)")
    ap.add_argument("--rows", type=int, default=500, help="How many bars to insert")
    ap.add_argument("--dsn", default="", help="Override DSN; defaults to config.yaml")
    args = ap.parse_args()

    symbol, interval = parse_pair(args.pair)
    dsn = args.dsn or _default_dsn()

    repo = TimescaleRepo(dsn)
    repo.connect()
    try:
        rows = _gen_rows(symbol, interval, max(10, args.rows))
        inserted = repo.upsert_klines(rows)
        # Update resume pointer to last close
        last_close = rows[-1]["close_time"]
        repo.set_last_closed_ts(symbol, interval, last_close)
        print(
            f"Seeded {inserted} rows for {symbol}/{interval} up to {last_close.isoformat()}"
        )
    finally:
        repo.close()


if __name__ == "__main__":
    main()
