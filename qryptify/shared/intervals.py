from __future__ import annotations

from datetime import timedelta

SUPPORTED_INTERVALS = (
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
)


def step_of(interval: str) -> timedelta:
    """Return the timedelta for a Binance kline interval string."""
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
    if interval not in table:
        raise ValueError(f"Unsupported interval: {interval}")
    return table[interval]


def validate_interval(interval: str) -> str:
    if interval not in SUPPORTED_INTERVALS:
        raise ValueError(f"Unsupported interval: {interval}")
    return interval
