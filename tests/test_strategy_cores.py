from __future__ import annotations

from qryptify_strategy.strategy_utils import BollingerCore
from qryptify_strategy.strategy_utils import EMACrossCore
from qryptify_strategy.strategy_utils import RSICore


def test_ema_cross_core_crosses():
    core = EMACrossCore(fast=3, slow=5)
    core.reset()
    ups = downs = 0
    for price in [1, 2, 3, 2, 1, 2, 3, 4]:
        res = core.update_and_cross(price)
        if res is None:
            continue
        up, dn = res
        ups += 1 if up else 0
        downs += 1 if dn else 0
    assert ups + downs >= 1


def test_bollinger_core_events_and_bands():
    core = BollingerCore(period=3, mult=2.0)
    core.reset()
    bands_seen = 0
    events_seen = 0
    seq = [1.0, 1.1, 1.2, 1.3, 1.1, 1.4]
    for c in seq:
        events, bands = core.update_and_events(c)
        if bands is not None:
            bands_seen += 1
        if any(events.values()):
            events_seen += 1
    assert bands_seen > 0


def test_rsi_core_basic_and_ema_filter():
    core = RSICore(period=5, ema_filter=3)
    core.reset()
    last = None
    for c in [1, 1.1, 1.2, 1.15, 1.25, 1.3, 1.35]:
        last = core.update(c)
    assert last is not None
    prev_rsi, rsi, ema_ok_long, ema_ok_short, ema_cross_down, ema_cross_up = last
    assert rsi is not None
    assert isinstance(ema_ok_long, bool) and isinstance(ema_ok_short, bool)
