from __future__ import annotations

import asyncio

from loguru import logger

from qryptify.ingestor.parsers import parse_ws_kline_row
from qryptify.ingestor.types import KlineRow
from qryptify.shared.pairs import symbol_interval_pairs_from_cfg


def _row_from_k(symbol: str, k: dict, interval: str) -> KlineRow:
    """Wrapper kept for compatibility; delegates to shared parser."""
    return parse_ws_kline_row(symbol, interval, k)


async def run_live(cfg, repo, client):
    pairs = symbol_interval_pairs_from_cfg(cfg)
    pairs_str = ", ".join([f"{s}/{i}" for s, i in pairs])
    logger.info(f"Live streaming started for: {pairs_str}")
    # Optional size-based buffering (default 1 = existing behavior)
    live_cfg = cfg.get("live", {}) if isinstance(cfg, dict) else {}
    try:
        buffer_max = int(live_cfg.get("buffer_max", 1))
    except Exception:
        buffer_max = 1
    buf: list[KlineRow] = []

    async for msg in client.ws_kline_stream_pairs(pairs):
        k = msg["k"]
        sym = msg["symbol"]
        if k.get("x") is True:
            interval = k.get("i")
            row = _row_from_k(sym, k, interval)
            buf.append(row)
            if len(buf) >= max(1, buffer_max):
                rows = buf
                buf = []
                if hasattr(repo, "upsert_klines_async"):
                    await repo.upsert_klines_async(rows)
                    # Update last close per last row in batch
                    last = rows[-1]
                    await repo.set_last_closed_ts_async(sym, interval,
                                                        last["close_time"])
                else:
                    await asyncio.to_thread(repo.upsert_klines, rows)
                    last = rows[-1]
                    await asyncio.to_thread(repo.set_last_closed_ts, sym, interval,
                                            last["close_time"])
                logger.debug(
                    f"Live close {sym}/{interval} at {row['close_time'].isoformat()} close={row['close']} batch={len(rows)}"
                )
