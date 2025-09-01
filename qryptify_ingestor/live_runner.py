from __future__ import annotations

from datetime import datetime
from datetime import timezone

from loguru import logger

from qryptify_shared.time import to_dt

from .config_utils import symbol_interval_pairs_from_cfg


def _row_from_k(symbol: str, k: dict, interval: str) -> dict:
    return {
        "ts": to_dt(k["t"]),
        "symbol": symbol,
        "interval": interval,
        "open": float(k["o"]),
        "high": float(k["h"]),
        "low": float(k["l"]),
        "close": float(k["c"]),
        "volume": float(k["v"]),
        "close_time": to_dt(k["T"]),
        "quote_asset_volume": float(k["q"]),
        "number_of_trades": int(k["n"]),
        "taker_buy_base": float(k["V"]),
        "taker_buy_quote": float(k["Q"]),
    }


async def run_live(cfg, repo, client):
    pairs = symbol_interval_pairs_from_cfg(cfg)
    pairs_str = ", ".join([f"{s}/{i}" for s, i in pairs])
    logger.info(f"Live streaming started for: {pairs_str}")

    async for msg in client.ws_kline_stream_pairs(pairs):
        k = msg["k"]
        sym = msg["symbol"]
        if k.get("x") is True:  # candle closed
            interval = k.get("i")
            row = _row_from_k(sym, k, interval)
            repo.upsert_klines([row])
            repo.set_last_closed_ts(sym, interval, row["close_time"])
            logger.debug(
                f"Live close {sym}/{interval} at {row['close_time'].isoformat()} close={row['close']}"
            )
