from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..indicators import ema
from ..indicators import WilderRSI
from ..models import Bar
from ..models import Signal
from ..strategy_base import Strategy


@dataclass
class RSIScalpStrategy(Strategy):
    """RSI mean-reversion with optional EMA filter (long/flat)."""

    rsi_period: int = 14
    entry: float = 30.0
    exit: float = 55.0
    ema_filter: int = 200  # set to 0 to disable filter
    id: str = "rsi_scalp"

    def __post_init__(self) -> None:
        if self.rsi_period <= 1:
            raise ValueError("rsi_period must be > 1")
        if not (0 < self.entry < 100) or not (0 < self.exit < 100):
            raise ValueError("entry/exit must be in (0, 100)")
        if self.exit <= self.entry:
            raise ValueError("exit must be > entry")
        self._rsi_calc = WilderRSI(self.rsi_period)
        self._rsi: Optional[float] = None
        self._ema: Optional[float] = None
        self._alpha_ema = 2.0 / (self.ema_filter +
                                 1.0) if self.ema_filter > 0 else 0.0
        self._last_close: Optional[float] = None

    def on_start(self) -> None:
        self._rsi_calc = WilderRSI(self.rsi_period)
        self._rsi = None
        self._ema = None
        self._last_close = None

    # RSI is provided by WilderRSI in indicators; no local implementation

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        prev_rsi = self._rsi
        prev_ema = self._ema
        prev_close = self._last_close if self._last_close is not None else bar.close

        rsi = self._rsi_calc.update(bar.close)
        self._rsi = rsi
        if self.ema_filter > 0:
            self._ema = ema(self._alpha_ema, self._ema, bar.close)

        signal: Optional[Signal] = None
        if rsi is None or prev_rsi is None:
            return None

        crossed_up_exit = prev_rsi <= self.exit and rsi > self.exit
        crossed_up_entry = prev_rsi <= self.entry and rsi > self.entry
        ema_ok = True if self.ema_filter <= 0 else (self._ema is not None
                                                    and bar.close > self._ema)
        ema_cross_down = False if self.ema_filter <= 0 else (
            prev_ema is not None and prev_close >= prev_ema
            and self._ema is not None and bar.close < self._ema)

        if crossed_up_exit:
            signal = Signal(target=0, reason="rsi_tp")
        elif crossed_up_entry and ema_ok:
            signal = Signal(target=+1, reason="rsi_rebound")
        elif ema_cross_down:
            signal = Signal(target=0, reason="ema_filter_exit")

        self._last_close = bar.close
        return signal
