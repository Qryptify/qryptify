from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional

from qryptify_strategy.backtester import backtest
from qryptify_strategy.models import Bar
from qryptify_strategy.models import RiskParams
from qryptify_strategy.models import Signal
from qryptify_strategy.strategy_base import Strategy


def _bars_series():
    # 5 bars, 1-minute apart
    base = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    bars = []
    prices = [
        (100.0, 100.5, 100.0, 100.0),  # i=0
        (100.0, 100.3, 99.8, 100.2),  # i=1
        (100.2, 100.5, 100.1, 100.3),  # i=2
        (100.3, 100.6, 100.2, 100.4),  # i=3
        (101.0, 101.1, 100.9, 101.0),  # i=4
    ]
    for i, (o, h, l, c) in enumerate(prices):
        bars.append(
            Bar(ts=base + timedelta(minutes=i),
                open=o,
                high=h,
                low=l,
                close=c,
                volume=0.0))
    return bars


@dataclass
class TestStrategy(Strategy):
    __test__ = False  # avoid pytest collecting this as a test class

    # Enter long at i=0, flatten at i=3
    def on_start(self) -> None:
        pass

    def on_bar(self, i: int, bar: Bar) -> Optional[Signal]:
        if i == 0:
            return Signal(target=+1, reason="enter")
        if i == 3:
            return Signal(target=0, reason="exit")
        return None

    def on_finish(self) -> None:
        pass


def test_backtest_entry_exit_and_pnl():
    bars = _bars_series()
    # ATR period=1 so it's available on first bar; slippage/fees zero
    risk = RiskParams(
        start_equity=10_000.0,
        risk_per_trade=0.01,
        atr_period=1,
        atr_mult_stop=1.0,
        fee_bps=0.0,
        slippage_bps=0.0,
    )
    rpt, trades = backtest("TEST", "1m", bars, TestStrategy(), risk)
    assert rpt.trades == 1
    t = trades[0]
    # Entry happens at next open after i=0 => bar[1].open
    assert t.entry_ts == bars[1].ts
    # Exit happens at next open after i=3 => bar[4].open
    assert t.exit_ts == bars[4].ts
    # Qty sizing: risk_cash / stop_dist where stop_dist = ATR(=0.5) * 1.0
    # First bar TR = high-low = 0.5
    expected_qty = (10_000.0 * 0.01) / 0.5
    assert abs(t.qty - expected_qty) < 1e-9
    # PnL = (exit - entry) * qty = (101.0 - 100.0) * expected_qty
    expected_pnl = (bars[4].open - bars[1].open) * expected_qty
    assert abs(t.pnl - expected_pnl) < 1e-6
