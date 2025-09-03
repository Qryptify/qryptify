from __future__ import annotations

from datetime import datetime
from datetime import timezone


def to_dt(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


__all__ = ["to_dt", "to_ms"]
