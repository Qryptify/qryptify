from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..indicators import RollingMeanStd
from ..models import Bar
from ..models import Signal
from ..strategy_base import Strategy


@dataclass
class BollingerBandStrategy(Strategy):
    """Bollinger Bands breakout (long/flat), signals on close."""

    period: int = 20
    mult: float = 2.0
    id: str = "bollinger"

    def __post_init__(self) -> None:
        if self.period <= 1:
            raise ValueError("period must be > 1")
        if self.mult <= 0:
            raise ValueError("mult must be > 0")
        self._roll = RollingMeanStd(self.period)
        self._prev_close: Optional[float] = None
        self._prev_mid: Optional[float] = None
        self._prev_upper: Optional[float] = None

    def on_start(self) -> None:
        self._roll.reset()
        self._prev_close = None
        self._prev_mid = None
        self._prev_upper = None

    def _current_bands(self,
                       close: float) -> Optional[tuple[float, float, float]]:
        stats = self._roll.update(close)
        if stats is None:
            return None
        mean, std = stats
        upper = mean + self.mult * std
        lower = mean - self.mult * std
        return lower, mean, upper

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        signal: Optional[Signal] = None

        if self._prev_close is not None and self._prev_upper is not None and self._prev_mid is not None:
            crossed_up_upper = self._prev_close <= self._prev_upper and bar.close > self._prev_upper
            crossed_below_mid = self._prev_close >= self._prev_mid and bar.close < self._prev_mid
            if crossed_up_upper:
                signal = Signal(target=+1, reason="bb_breakout_up")
            elif crossed_below_mid:
                signal = Signal(target=0, reason="bb_cross_below_mid")

        bands = self._current_bands(bar.close)
        if bands is not None:
            _, mid, upper = bands
            self._prev_mid = mid
            self._prev_upper = upper
        else:
            self._prev_mid = None
            self._prev_upper = None

        self._prev_close = bar.close
        return signal
