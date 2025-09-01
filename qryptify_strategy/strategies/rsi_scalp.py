from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..models import Bar
from ..models import Signal
from ..strategy_base import Strategy
from ..strategy_utils import RSICore


@dataclass
class RSIScalpStrategy(Strategy):
    """RSI mean-reversion with optional EMA filter (long/flat)."""

    rsi_period: int = 14
    entry: float = 30.0
    exit: float = 55.0
    ema_filter: int = 200  # set to 0 to disable filter
    id: str = "rsi_scalp"

    def __post_init__(self) -> None:
        if not (0 < self.entry < 100) or not (0 < self.exit < 100):
            raise ValueError("entry/exit must be in (0, 100)")
        if self.exit <= self.entry:
            raise ValueError("exit must be > entry")
        self._core = RSICore(self.rsi_period, self.ema_filter)

    def on_start(self) -> None:
        self._core.reset()

    # RSI is provided by WilderRSI in indicators; no local implementation

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        prev_rsi, rsi, ema_ok_long, _ema_ok_short, ema_cross_down, _ema_cross_up = self._core.update(
            bar.close)
        if rsi is None or prev_rsi is None:
            return None
        signal: Optional[Signal] = None
        crossed_up_exit = prev_rsi <= self.exit and rsi > self.exit
        crossed_up_entry = prev_rsi <= self.entry and rsi > self.entry
        if crossed_up_exit:
            signal = Signal(target=0, reason="rsi_tp")
        elif crossed_up_entry and ema_ok_long:
            signal = Signal(target=+1, reason="rsi_rebound")
        elif ema_cross_down:
            signal = Signal(target=0, reason="ema_filter_exit")
        return signal
