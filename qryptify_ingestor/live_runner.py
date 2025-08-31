from __future__ import annotations

from datetime import datetime
from datetime import timezone

from loguru import logger


def _to_dt(ms: int):  # shared tiny helper
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def _row_from_k(symbol: str, k: dict, interval: str) -> dict:
    return {
        "ts": _to_dt(k["t"]),
        "symbol": symbol,
        "interval": interval,
        "open": k["o"],
        "high": k["h"],
        "low": k["l"],
        "close": k["c"],
        "volume": k["v"],
        "close_time": _to_dt(k["T"]),
        "quote_asset_volume": k["q"],
        "number_of_trades": int(k["n"]),
        "taker_buy_base": k["V"],
        "taker_buy_quote": k["Q"],
    }


async def run_live(cfg, repo, client):
    symbols = cfg["symbols"]
    intervals = cfg["intervals"]
    assert len(intervals) == 1, "MVP: single interval for WS"
    itv = intervals[0]
    logger.info(f"Live streaming started for {symbols} at interval {itv}")

    async for msg in client.ws_kline_stream(symbols, itv):
        k = msg["k"]
        sym = msg["symbol"]
        if k.get("x") is True:  # candle closed
            row = _row_from_k(sym, k, itv)
            repo.upsert_klines([row])
            repo.set_last_closed_ts(sym, itv, row["close_time"])
            logger.debug(
                f"Live close {sym}/{itv} at {row['close_time'].isoformat()} close={row['close']}"
            )
