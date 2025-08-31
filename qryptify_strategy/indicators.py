from __future__ import annotations

from collections import deque
from typing import Deque, Optional


def ema(alpha: float, prev: Optional[float], value: float) -> float:
    """Exponential moving average update."""
    if prev is None:
        return value
    return alpha * value + (1.0 - alpha) * prev


class WilderRSI:
    """Wilder's RSI with warm-up; update(close)->RSI or None."""

    def __init__(self, period: int) -> None:
        if period <= 1:
            raise ValueError("period must be > 1")
        self.period = period
        self._prev_close: Optional[float] = None
        self._sum_gain = 0.0
        self._sum_loss = 0.0
        self._avg_gain: Optional[float] = None
        self._avg_loss: Optional[float] = None
        self._count = 0

    def reset(self) -> None:
        self._prev_close = None
        self._sum_gain = 0.0
        self._sum_loss = 0.0
        self._avg_gain = None
        self._avg_loss = None
        self._count = 0

    def update(self, close: float) -> Optional[float]:
        prev = self._prev_close
        if prev is None:
            self._prev_close = close
            return None

        change = close - prev
        gain = change if change > 0 else 0.0
        loss = -change if change < 0 else 0.0

        if self._avg_gain is None or self._avg_loss is None:
            # Warm-up: accumulate first `period` diffs
            self._sum_gain += gain
            self._sum_loss += loss
            self._count += 1
            if self._count < self.period:
                self._prev_close = close
                return None
            # Initialize averages
            self._avg_gain = self._sum_gain / float(self.period)
            self._avg_loss = self._sum_loss / float(self.period)
        else:
            # Wilder smoothing
            self._avg_gain = (self._avg_gain *
                              (self.period - 1) + gain) / self.period
            self._avg_loss = (self._avg_loss *
                              (self.period - 1) + loss) / self.period

        # Compute RSI from averages
        if self._avg_loss == 0.0 and self._avg_gain == 0.0:
            rsi = 50.0
        elif self._avg_loss == 0.0:
            rsi = 100.0
        else:
            rs = self._avg_gain / self._avg_loss
            rsi = 100.0 - (100.0 / (1.0 + rs))

        self._prev_close = close
        return rsi


def true_range(high: float, low: float, prev_close: Optional[float]) -> float:
    """True range = max(high-low, |high-pc|, |low-pc|)."""
    if prev_close is None:
        return high - low
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


class WilderATR:
    """Wilder's ATR; update(tr)->ATR or None during warm-up."""

    def __init__(self, period: int) -> None:
        if period <= 0:
            raise ValueError("period must be > 0")
        self.period = period
        self._count = 0
        self._atr: Optional[float] = None
        self._sum_tr = 0.0

    def reset(self) -> None:
        self._count = 0
        self._atr = None
        self._sum_tr = 0.0

    def update(self, tr: float) -> Optional[float]:
        self._count += 1
        if self._count <= self.period:
            self._sum_tr += tr
            if self._count == self.period:
                self._atr = self._sum_tr / self.period
            return self._atr
        self._atr = ((self._atr or tr) * (self.period - 1) + tr) / self.period
        return self._atr


class RollingMeanStd:
    """Fixed-window mean/std (population). update(x)->(mean,std) or None."""

    def __init__(self, period: int) -> None:
        if period <= 1:
            raise ValueError("period must be > 1")
        self.period = period
        self._win: Deque[float] = deque()
        self._sum = 0.0
        self._sumsq = 0.0

    def reset(self) -> None:
        self._win.clear()
        self._sum = 0.0
        self._sumsq = 0.0

    def update(self, value: float) -> Optional[tuple[float, float]]:
        self._win.append(value)
        self._sum += value
        self._sumsq += value * value
        if len(self._win) > self.period:
            old = self._win.popleft()
            self._sum -= old
            self._sumsq -= old * old
        if len(self._win) < self.period:
            return None
        n = self.period
        mean = self._sum / n
        var = max(self._sumsq / n - mean * mean, 0.0)
        std = var**0.5
        return mean, std
