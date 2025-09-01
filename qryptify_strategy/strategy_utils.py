from __future__ import annotations

from typing import Optional, Tuple

from .indicators import ema


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
