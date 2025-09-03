from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional, Protocol, TypedDict


class KlineRow(TypedDict):
    ts: datetime
    symbol: str
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base: float
    taker_buy_quote: float


class TimescaleWriter(Protocol):

    def upsert_klines(self, rows: Iterable[KlineRow]) -> int:
        ...

    def set_last_closed_ts(self, symbol: str, interval: str, ts: datetime) -> None:
        ...


class TimescaleReader(Protocol):

    def fetch_ohlcv(
        self,
        symbol: str,
        interval: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[dict]:
        ...

    def fetch_latest_n(self, symbol: str, interval: str, n: int) -> List[dict]:
        ...

    def get_last_closed_ts(self, symbol: str, interval: str) -> Optional[datetime]:
        ...
