from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..indicators import ema
from ..indicators import WilderRSI
from ..models import Bar
from ..models import Signal
from ..strategy_base import Strategy


@dataclass
class RSITwoSidedStrategy(Strategy):
    """Two-sided RSI mean-reversion with optional EMA regime filter.

    Long logic:
      - Enter when RSI crosses up entry_low (e.g., 30), optional filter close>EMA
      - Exit when RSI crosses up exit_low (e.g., 55) or EMA crosses down if filter

    Short logic:
      - Enter when RSI crosses down entry_high (e.g., 70), optional filter close<EMA
      - Exit when RSI crosses down exit_high (e.g., 45) or EMA crosses up if filter
    """

    rsi_period: int = 14
    entry_low: float = 30.0
    exit_low: float = 55.0
    entry_high: float = 70.0
    exit_high: float = 45.0
    ema_filter: int = 0  # 0 disables regime filter
    id: str = "rsi_ls"

    def __post_init__(self) -> None:
        if self.rsi_period <= 1:
            raise ValueError("rsi_period must be > 1")
        for v in (self.entry_low, self.exit_low, self.entry_high,
                  self.exit_high):
            if not (0 < v < 100):
                raise ValueError("RSI thresholds must be in (0, 100)")
        self._rsi_calc = WilderRSI(self.rsi_period)
        self._rsi: Optional[float] = None
        self._ema: Optional[float] = None
        self._alpha_ema = (2.0 / (self.ema_filter + 1.0)
                           if self.ema_filter > 0 else 0.0)
        self._last_close: Optional[float] = None

    def on_start(self) -> None:
        self._rsi_calc = WilderRSI(self.rsi_period)
        self._rsi = None
        self._ema = None
        self._last_close = None

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        prev_rsi = self._rsi
        prev_ema = self._ema
        prev_close = self._last_close if self._last_close is not None else bar.close

        rsi = self._rsi_calc.update(bar.close)
        self._rsi = rsi
        if self.ema_filter > 0:
            self._ema = ema(self._alpha_ema, self._ema, bar.close)

        if rsi is None or prev_rsi is None:
            self._last_close = bar.close
            return None

        crossed_up_exit_low = prev_rsi <= self.exit_low and rsi > self.exit_low
        crossed_up_entry_low = prev_rsi <= self.entry_low and rsi > self.entry_low
        crossed_down_exit_high = prev_rsi >= self.exit_high and rsi < self.exit_high
        crossed_down_entry_high = prev_rsi >= self.entry_high and rsi < self.entry_high

        ema_ok_long = True if self.ema_filter <= 0 else (
            self._ema is not None and bar.close > self._ema)
        ema_ok_short = True if self.ema_filter <= 0 else (
            self._ema is not None and bar.close < self._ema)
        ema_cross_down = False if self.ema_filter <= 0 else (
            prev_ema is not None and prev_close >= prev_ema
            and self._ema is not None and bar.close < self._ema)
        ema_cross_up = False if self.ema_filter <= 0 else (
            prev_ema is not None and prev_close <= prev_ema
            and self._ema is not None and bar.close > self._ema)

        signal: Optional[Signal] = None
        # Exits take precedence
        if crossed_up_exit_low or ema_cross_down:
            signal = Signal(target=0, reason="rsi_long_exit")
        elif crossed_down_exit_high or ema_cross_up:
            signal = Signal(target=0, reason="rsi_short_exit")
        elif crossed_up_entry_low and ema_ok_long:
            signal = Signal(target=+1, reason="rsi_long_entry")
        elif crossed_down_entry_high and ema_ok_short:
            signal = Signal(target=-1, reason="rsi_short_entry")

        self._last_close = bar.close
        return signal
