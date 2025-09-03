from __future__ import annotations

import json
import time
from typing import Dict, Tuple

_DEFAULT_MAKER_BPS = 2.0
_DEFAULT_TAKER_BPS = 4.0

_CACHE: Dict[str, Tuple[float, float, float]] = {}


def _fetch_fee_bps_httpx(symbol: str, timeout: float) -> Tuple[float, float]:
    """Try to fetch fees using httpx if available; raise on error."""
    try:
        import httpx
    except Exception as e:
        raise RuntimeError("httpx not available") from e
    url = f"https://fapi.binance.com/fapi/v1/commissionRate?symbol={symbol.upper()}"
    with httpx.Client(timeout=timeout) as cli:
        r = cli.get(url)
        r.raise_for_status()
        data = r.json()
    maker = float(data.get("makerCommissionRate", 0.0002)) * 10_000.0
    taker = float(data.get("takerCommissionRate", 0.0004)) * 10_000.0
    return maker, taker


def _fetch_fee_bps_urllib(symbol: str, timeout: float) -> Tuple[float, float]:
    """Fallback fetch using stdlib urllib if httpx is unavailable."""
    from urllib.request import urlopen

    url = f"https://fapi.binance.com/fapi/v1/commissionRate?symbol={symbol.upper()}"
    with urlopen(url, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    maker = float(data.get("makerCommissionRate", 0.0002)) * 10_000.0
    taker = float(data.get("takerCommissionRate", 0.0004)) * 10_000.0
    return maker, taker


def binance_futures_fee_bps(symbol: str,
                            *,
                            timeout_s: float = 10.0,
                            ttl_seconds: float = 3600.0) -> Tuple[float, float]:
    """Fetch maker/taker commission rates for Binance USDT‑M futures in bps.

    - Returns a tuple (maker_bps, taker_bps).
    - Uses a simple in‑process TTL cache (default 1 hour) per symbol.
    - Falls back to (2.0, 4.0) on any error.
    - Prefers httpx if installed; otherwise uses urllib.
    """
    sym = symbol.upper()
    now = time.monotonic()
    cached = _CACHE.get(sym)
    if cached and cached[2] > now:
        return cached[0], cached[1]

    try:
        try:
            maker, taker = _fetch_fee_bps_httpx(sym, timeout_s)
        except Exception:
            maker, taker = _fetch_fee_bps_urllib(sym, timeout_s)
        exp = now + max(ttl_seconds, 60.0)
        _CACHE[sym] = (maker, taker, exp)
        return maker, taker
    except Exception:
        return _DEFAULT_MAKER_BPS, _DEFAULT_TAKER_BPS
