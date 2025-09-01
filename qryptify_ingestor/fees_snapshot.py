from __future__ import annotations

import argparse
from datetime import datetime
from datetime import timezone
from typing import List, Tuple

import yaml

from qryptify_ingestor.config_utils import parse_pair
from qryptify_ingestor.config_utils import symbol_interval_pairs_from_cfg
from qryptify_strategy.fees import binance_futures_fee_bps

from .timescale_repo import TimescaleRepo


def main() -> None:
    p = argparse.ArgumentParser(description="Snapshot Binance futures fees into DB")
    p.add_argument("--config",
                   default="qryptify_ingestor/config.yaml",
                   help="Config YAML (reads DB dsn and pairs)")
    p.add_argument(
        "--pairs",
        default="",
        help="Optional comma-separated SYMBOL/interval list; overrides config pairs")
    p.add_argument("--show",
                   action="store_true",
                   help="Print rows that would be written")
    p.add_argument("--dry-run",
                   action="store_true",
                   help="Show rows and exit without writing to DB")
    args = p.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f) or {}
    dsn = cfg.get("db", {}).get("dsn")
    if not dsn:
        raise SystemExit("DB DSN not found in config")

    if args.pairs:
        pair_strs = [s.strip() for s in args.pairs.split(",") if s.strip()]
        pairs = [parse_pair(p) for p in pair_strs]
    else:
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f) or {}
        pairs = symbol_interval_pairs_from_cfg(cfg)
    symbols = sorted({sym for sym, _ in pairs})

    now_ts = datetime.now(timezone.utc)
    rows = []
    for sym in symbols:
        maker, taker = binance_futures_fee_bps(sym)
        rows.append({
            "ts": now_ts,
            "symbol": sym,
            "maker_bps": maker,
            "taker_bps": taker,
            "source": "binance_fapi",
            "note": None,
        })

    if args.show or args.dry_run:
        print("Fee snapshots:")
        for r in rows:
            print(
                f"  ts={r['ts'].isoformat()} symbol={r['symbol']} maker_bps={r['maker_bps']:.4f} taker_bps={r['taker_bps']:.4f} source={r['source']}"
            )
    if args.dry_run:
        print("Dry run: not writing to DB")
        return

    repo = TimescaleRepo(dsn)
    repo.connect()
    try:
        repo.ensure_exchange_fees_schema()
        n = repo.upsert_exchange_fees(rows)
        print(f"Inserted/updated {n} fee snapshots at {now_ts.isoformat()}")
    finally:
        repo.close()


if __name__ == "__main__":
    main()
