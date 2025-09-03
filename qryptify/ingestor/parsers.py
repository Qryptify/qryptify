from __future__ import annotations

from typing import Dict

from qryptify.shared.time import to_dt

from .types import KlineRow


def parse_rest_kline_row(symbol: str, interval: str, arr: list) -> KlineRow:
    """Parse a REST kline array into a DB row dict.

    Binance kline schema indices:
    0 open time(ms), 1 open, 2 high, 3 low, 4 close, 5 volume,
    6 close time(ms), 7 quote asset vol, 8 trades, 9 taker buy base,
    10 taker buy quote, 11 ignore
    """
    return KlineRow(
        ts=to_dt(arr[0]),
        symbol=symbol,
        interval=interval,
        open=float(arr[1]),
        high=float(arr[2]),
        low=float(arr[3]),
        close=float(arr[4]),
        volume=float(arr[5]),
        close_time=to_dt(arr[6]),
        quote_asset_volume=float(arr[7]),
        number_of_trades=int(arr[8]),
        taker_buy_base=float(arr[9]),
        taker_buy_quote=float(arr[10]),
    )


def parse_ws_kline_row(symbol: str, interval: str, k: Dict) -> KlineRow:
    return KlineRow(
        ts=to_dt(k["t"]),
        symbol=symbol,
        interval=interval,
        open=float(k["o"]),
        high=float(k["h"]),
        low=float(k["l"]),
        close=float(k["c"]),
        volume=float(k["v"]),
        close_time=to_dt(k["T"]),
        quote_asset_volume=float(k["q"]),
        number_of_trades=int(k["n"]),
        taker_buy_base=float(k["V"]),
        taker_buy_quote=float(k["Q"]),
    )
