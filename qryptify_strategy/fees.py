from __future__ import annotations

from functools import lru_cache
import json
from typing import Tuple
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
