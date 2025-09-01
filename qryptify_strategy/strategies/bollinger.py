from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..models import Bar
from ..models import Signal
from ..strategy_base import Strategy
from ..strategy_utils import BollingerCore


@dataclass
class BollingerBandStrategy(Strategy):
    """Bollinger Bands breakout (long/flat), signals on close."""

    period: int = 20
    mult: float = 2.0
    id: str = "bollinger"

    def __post_init__(self) -> None:
        self._core = BollingerCore(self.period, self.mult)

    def on_start(self) -> None:
        self._core.reset()

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        signal: Optional[Signal] = None
        events, _ = self._core.update_and_events(bar.close)
        if events.get("cross_up_upper"):
            signal = Signal(target=+1, reason="bb_breakout_up")
        elif events.get("cross_below_mid"):
            signal = Signal(target=0, reason="bb_cross_below_mid")
        return signal
