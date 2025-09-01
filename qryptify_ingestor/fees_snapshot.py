from __future__ import annotations

import argparse
from datetime import datetime
from datetime import timezone
from typing import List, Tuple

import yaml

from qryptify_strategy.fees import binance_futures_fee_bps

from .timescale_repo import TimescaleRepo


def _parse_pair(pair: str) -> Tuple[str, str]:
    if "/" in pair:
        s, i = pair.split("/", 1)
    elif "-" in pair:
        s, i = pair.split("-", 1)
    else:
        raise ValueError("pair must be SYMBOL/interval or SYMBOL-interval")
    return s.upper(), i


def _load_cfg_pairs(path: str) -> List[str]:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f) or {}
    pairs_raw = cfg.get("pairs") or []
    pairs: List[str] = []
    for p in pairs_raw:
        if isinstance(p, dict):
            sym = str(p.get("symbol", "")).strip()
            ivl = str(p.get("interval", "")).strip()
            if sym and ivl:
                pairs.append(f"{sym}/{ivl}")
                continue
        pairs.append(str(p))
    return pairs


def main() -> None:
    p = argparse.ArgumentParser(
        description="Snapshot Binance futures fees into DB")
    p.add_argument("--config",
                   default="qryptify_ingestor/config.yaml",
                   help="Config YAML (reads DB dsn and pairs)")
    p.add_argument(
        "--pairs",
        default="",
        help=
        "Optional comma-separated SYMBOL/interval list; overrides config pairs"
    )
    args = p.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f) or {}
    dsn = cfg.get("db", {}).get("dsn")
    if not dsn:
        raise SystemExit("DB DSN not found in config")

    pairs = ([s.strip() for s in args.pairs.split(",")
              if s.strip()] if args.pairs else _load_cfg_pairs(args.config))
    symbols = sorted({_parse_pair(p)[0] for p in pairs})

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

    repo = TimescaleRepo(dsn)
    repo.connect()
    try:
        # Ensure table exists (idempotent)
        ddl = (
            "CREATE TABLE IF NOT EXISTS exchange_fees (\n"
            "  ts TIMESTAMPTZ NOT NULL,\n"
            "  symbol TEXT NOT NULL CHECK (symbol = upper(symbol)),\n"
            "  maker_bps DOUBLE PRECISION NOT NULL,\n"
            "  taker_bps DOUBLE PRECISION NOT NULL,\n"
            "  source TEXT NOT NULL DEFAULT 'binance_fapi',\n"
            "  note TEXT,\n"
            "  PRIMARY KEY (symbol, ts)\n"
            ");\n"
            "SELECT create_hypertable('exchange_fees', 'ts', if_not_exists => TRUE, chunk_time_interval => INTERVAL '30 days');\n"
            "CREATE INDEX IF NOT EXISTS idx_exchange_fees_symbol_ts ON exchange_fees(symbol, ts DESC);"
        )
        conn = repo._require_conn()  # type: ignore
        with conn.cursor() as cur:
            for stmt in ddl.split(";\n"):
                s = stmt.strip()
                if s:
                    cur.execute(s)
            conn.commit()
        n = repo.upsert_exchange_fees(rows)
        print(f"Inserted/updated {n} fee snapshots at {now_ts.isoformat()}")
    finally:
        repo.close()


if __name__ == "__main__":
    main()
