from __future__ import annotations

from typing import Optional, Tuple

from .indicators import ema
from .indicators import RollingMeanStd
from .indicators import WilderRSI


class EMACrossCore:
    """Reusable EMA crossover core that tracks fast/slow EMAs and detects crosses.

    Usage:
      core = EMACrossCore(fast=50, slow=200)
      core.reset()
      res = core.update_and_cross(price)
      if res is not None:
          crossed_up, crossed_dn = res
    """

    def __init__(self, fast: int, slow: int) -> None:
        if fast >= slow:
            raise ValueError("fast period must be < slow period")
        self.fast = fast
        self.slow = slow
        self._fast_ema: Optional[float] = None
        self._slow_ema: Optional[float] = None
        self._alpha_fast = 2.0 / (self.fast + 1.0)
        self._alpha_slow = 2.0 / (self.slow + 1.0)

    def reset(self) -> None:
        self._fast_ema = None
        self._slow_ema = None

    def update_and_cross(self, price: float) -> Optional[Tuple[bool, bool]]:
        prev_fast = self._fast_ema
        prev_slow = self._slow_ema
        self._fast_ema = ema(self._alpha_fast, self._fast_ema, price)
        self._slow_ema = ema(self._alpha_slow, self._slow_ema, price)
        if prev_fast is None or prev_slow is None:
            return None
        crossed_up = prev_fast <= prev_slow and self._fast_ema > self._slow_ema
        crossed_dn = prev_fast >= prev_slow and self._fast_ema < self._slow_ema
        return crossed_up, crossed_dn


class BollingerCore:
    """Reusable Bollinger Bands core with previous-band event detection.

    Computes rolling mean/std bands and tracks prior close and bands to emit
    crossing events that match existing strategies' semantics.
    """

    def __init__(self, period: int, mult: float) -> None:
        if period <= 1:
            raise ValueError("period must be > 1")
        if mult <= 0:
            raise ValueError("mult must be > 0")
        self.period = period
        self.mult = mult
        self._roll = RollingMeanStd(period)
        self._prev_close: Optional[float] = None
        self._prev_lower: Optional[float] = None
        self._prev_mid: Optional[float] = None
        self._prev_upper: Optional[float] = None

    def reset(self) -> None:
        self._roll.reset()
        self._prev_close = None
        self._prev_lower = None
        self._prev_mid = None
        self._prev_upper = None

    def update_and_events(
            self,
            close: float) -> Tuple[dict, Optional[Tuple[float, float, float]]]:
        events = {
            "cross_up_upper": False,
            "cross_down_lower": False,
            "cross_below_mid": False,
            "cross_above_mid": False,
        }
        if (self._prev_close is not None and self._prev_mid is not None
                and self._prev_upper is not None
                and self._prev_lower is not None):
            events[
                "cross_up_upper"] = self._prev_close <= self._prev_upper and close > self._prev_upper
            events[
                "cross_down_lower"] = self._prev_close >= self._prev_lower and close < self._prev_lower
            events[
                "cross_below_mid"] = self._prev_close >= self._prev_mid and close < self._prev_mid
            events[
                "cross_above_mid"] = self._prev_close <= self._prev_mid and close > self._prev_mid

        stats = self._roll.update(close)
        if stats is not None:
            mean, std = stats
            upper = mean + self.mult * std
            lower = mean - self.mult * std
            self._prev_lower = lower
            self._prev_mid = mean
            self._prev_upper = upper
            bands = (lower, mean, upper)
        else:
            self._prev_lower = None
            self._prev_mid = None
            self._prev_upper = None
            bands = None
        self._prev_close = close
        return events, bands


class RSICore:
    """Reusable RSI + optional EMA filter core that exposes crossings.

    update(close) returns a tuple of:
      (prev_rsi, rsi, ema_ok_long, ema_ok_short, ema_cross_down, ema_cross_up)
    """

    def __init__(self, period: int, ema_filter: int) -> None:
        if period <= 1:
            raise ValueError("period must be > 1")
        self.period = period
        self.ema_filter = ema_filter
        self._rsi_calc = WilderRSI(period)
        self._rsi: Optional[float] = None
        self._ema: Optional[float] = None
        self._alpha_ema = 2.0 / (ema_filter + 1.0) if ema_filter > 0 else 0.0
        self._last_close: Optional[float] = None

    def reset(self) -> None:
        self._rsi_calc = WilderRSI(self.period)
        self._rsi = None
        self._ema = None
        self._last_close = None

    def update(self, close: float):
        prev_rsi = self._rsi
        prev_ema = self._ema
        prev_close = self._last_close if self._last_close is not None else close

        rsi = self._rsi_calc.update(close)
        self._rsi = rsi
        if self.ema_filter > 0:
            self._ema = ema(self._alpha_ema, self._ema, close)

        ema_ok_long = True if self.ema_filter <= 0 else (self._ema is not None
                                                         and close > self._ema)
        ema_ok_short = True if self.ema_filter <= 0 else (
            self._ema is not None and close < self._ema)
        ema_cross_down = False if self.ema_filter <= 0 else (
            prev_ema is not None and prev_close >= prev_ema
            and self._ema is not None and close < self._ema)
        ema_cross_up = False if self.ema_filter <= 0 else (
            prev_ema is not None and prev_close <= prev_ema
            and self._ema is not None and close > self._ema)

        self._last_close = close
        return prev_rsi, rsi, ema_ok_long, ema_ok_short, ema_cross_down, ema_cross_up
