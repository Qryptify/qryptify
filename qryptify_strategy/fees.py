from __future__ import annotations

import bisect
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
import json
from typing import Iterable, List, Sequence, Tuple
from urllib.request import urlopen


@lru_cache(maxsize=128)
def binance_futures_fee_bps(symbol: str) -> Tuple[float, float]:
    """Fetch maker/taker commission rates for Binance USDT‑M futures in bps.

    Returns (maker_bps, taker_bps). Falls back to (2.0, 4.0) on error.
    """
    url = (f"https://fapi.binance.com/fapi/v1/commissionRate?symbol={symbol.upper()}")
    try:
        with urlopen(url, timeout=10) as resp:  # nosec B310 - public API URL
            data = json.loads(resp.read().decode())
        maker = float(data.get("makerCommissionRate", 0.0002)) * 10_000.0
        taker = float(data.get("takerCommissionRate", 0.0004)) * 10_000.0
        return maker, taker
    except Exception:
        # Default Binance base tier if request fails
        return 2.0, 4.0


@dataclass
class FeeSnapshot:
    ts: datetime
    maker_bps: float
    taker_bps: float


class FeeLookup:
    """Binary-search lookup for time-varying fees.

    snapshots: ascending by ts. Returns maker/taker bps at or before given ts.
    """

    def __init__(self, snapshots: Sequence[FeeSnapshot]):
        snaps = sorted(snapshots, key=lambda s: s.ts)
        self._ts: List[datetime] = [s.ts for s in snaps]
        self._maker: List[float] = [s.maker_bps for s in snaps]
        self._taker: List[float] = [s.taker_bps for s in snaps]

    def __bool__(self) -> bool:
        return len(self._ts) > 0

    def get_bps(self, ts: datetime, prefer_taker: bool = True) -> float:
        if not self._ts:
            return 0.0
        i = bisect.bisect_right(self._ts, ts) - 1
        if i < 0:
            i = 0
        return self._taker[i] if prefer_taker else self._maker[i]


def build_fee_lookup_from_rows(rows: Iterable[dict]) -> FeeLookup:
    snaps = [
        FeeSnapshot(ts=r["ts"],
                    maker_bps=float(r["maker_bps"]),
                    taker_bps=float(r["taker_bps"])) for r in rows
    ]
    return FeeLookup(snaps)
