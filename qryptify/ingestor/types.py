from __future__ import annotations

from datetime import datetime
from typing import TypedDict


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
