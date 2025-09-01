from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..models import Bar
from ..models import Signal
from ..strategy_base import Strategy
from ..strategy_utils import EMACrossCore


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
        self._core = EMACrossCore(self.fast, self.slow)

    def on_start(self) -> None:
        self._core.reset()

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        res = self._core.update_and_cross(bar.close)
        if res is None:
            return None
        crossed_up, crossed_dn = res

        if crossed_up:
            return Signal(target=+1, reason="fast_cross_above_slow")
        if crossed_dn:
            return Signal(target=-1, reason="fast_cross_below_slow")
        return None
