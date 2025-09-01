from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..indicators import ema
from ..models import Bar
from ..models import Signal
from ..strategy_base import Strategy


@dataclass
class EMACrossLongShortStrategy(Strategy):
    """Two-sided EMA crossover (long/short).

    Signals on close:
    - Cross fast above slow -> target +1 (long)
    - Cross fast below slow -> target -1 (short)
    Otherwise returns None to keep current exposure.
    """

    fast: int = 50
    slow: int = 200
    id: str = "ema_cross_long_short"

    def __post_init__(self) -> None:
        if self.fast >= self.slow:
            raise ValueError("fast period must be < slow period")
        self._fast_ema: Optional[float] = None
        self._slow_ema: Optional[float] = None
        self._alpha_fast = 2.0 / (self.fast + 1.0)
        self._alpha_slow = 2.0 / (self.slow + 1.0)

    def on_start(self) -> None:
        self._fast_ema = None
        self._slow_ema = None

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        price = bar.close
        prev_fast = self._fast_ema
        prev_slow = self._slow_ema

        self._fast_ema = ema(self._alpha_fast, self._fast_ema, price)
        self._slow_ema = ema(self._alpha_slow, self._slow_ema, price)

        if prev_fast is None or prev_slow is None:
            return None

        crossed_up = prev_fast <= prev_slow and self._fast_ema > self._slow_ema
        crossed_dn = prev_fast >= prev_slow and self._fast_ema < self._slow_ema

        if crossed_up:
            return Signal(target=+1, reason="fast_cross_above_slow")
        if crossed_dn:
            return Signal(target=-1, reason="fast_cross_below_slow")
        return None
