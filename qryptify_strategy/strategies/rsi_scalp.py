from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..models import Bar
from ..models import Signal
from ..strategy_base import Strategy
from ..strategy_utils import RSICore


@dataclass
class RSIScalpStrategy(Strategy):

    rsi_period: int = 14
    entry: float = 30.0
    exit: float = 55.0
    ema_filter: int = 200

    def __post_init__(self) -> None:
        if not (0 < self.entry < 100) or not (0 < self.exit < 100):
            raise ValueError("entry/exit must be in (0, 100)")
        if self.exit <= self.entry:
            raise ValueError("exit must be > entry")
        self._core = RSICore(self.rsi_period, self.ema_filter)

    def on_start(self) -> None:
        self._core.reset()

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        prev_rsi, rsi, ema_ok_long, ema_ok_short, ema_cross_down, ema_cross_up = self._core.update(
            bar.close)
        if rsi is None or prev_rsi is None:
            return None

        entry_low = self.entry
        exit_low = self.exit
        entry_high = max(70.0, 100.0 - self.entry)
        exit_high = min(55.0, 100.0 - self.exit)

        crossed_up_exit_low = prev_rsi <= exit_low and rsi > exit_low
        crossed_up_entry_low = prev_rsi <= entry_low and rsi > entry_low
        crossed_down_exit_high = prev_rsi >= exit_high and rsi < exit_high
        crossed_down_entry_high = prev_rsi >= entry_high and rsi < entry_high

        if crossed_up_exit_low or ema_cross_down:
            return Signal(target=0, reason="rsi_long_exit")
        if crossed_down_exit_high or ema_cross_up:
            return Signal(target=0, reason="rsi_short_exit")
        if crossed_up_entry_low and ema_ok_long:
            return Signal(target=+1, reason="rsi_long_entry")
        if crossed_down_entry_high and ema_ok_short:
            return Signal(target=-1, reason="rsi_short_entry")
        return None
