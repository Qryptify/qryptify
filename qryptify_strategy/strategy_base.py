from __future__ import annotations

from typing import Optional

from .models import Bar
from .models import Signal


class Strategy:
    """Base bar-close strategy interface.

    Implementations operate on closed bars and return a target exposure
    signal (-1/0/+1). Sizing and risk are handled by the executor/backtester.
    """

    id: str = "base"

    def on_start(self) -> None:
        pass

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        raise NotImplementedError

    def on_finish(self) -> None:
        pass
