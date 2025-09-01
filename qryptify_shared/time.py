from __future__ import annotations

from datetime import datetime
from datetime import timezone


def to_dt(ms: int) -> datetime:
    """Convert millisecond epoch to timezone-aware UTC datetime."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def to_ms(dt: datetime) -> int:
    """Convert timezone-aware datetime to millisecond epoch (UTC)."""
    return int(dt.timestamp() * 1000)
