from __future__ import annotations

from math import isclose

from qryptify_strategy.indicators import ema
from qryptify_strategy.indicators import RollingMeanStd
from qryptify_strategy.indicators import true_range
from qryptify_strategy.indicators import WilderATR
from qryptify_strategy.indicators import WilderRSI


def test_ema_basic():
    prev = None
    alpha = 0.5
    # First value: seed to value
    prev = ema(alpha, prev, 10.0)
    assert prev == 10.0
    # Next update: 0.5*12 + 0.5*10 = 11
    nxt = ema(alpha, prev, 12.0)
    assert isclose(nxt, 11.0, rel_tol=1e-9)


def test_true_range_cases():
    # No prev close
    assert isclose(true_range(10.0, 8.0, None), 2.0)
    # With prev close inside range
    assert isclose(true_range(10.0, 8.0, 9.0), 2.0)
    # With prev close above high
    assert isclose(true_range(10.0, 8.0, 11.0), 3.0)
    # With prev close below low
    assert isclose(true_range(10.0, 8.0, 7.0), 3.0)


def test_wilder_rsi_warmup_and_range():
    r = WilderRSI(14)
    vals = [i for i in range(100, 120)]  # increasing closes
    last = None
    for v in vals:
        last = r.update(v)
    # After warm-up, RSI should be defined and > 50 for uptrend
    assert last is not None
    assert 50.0 < last <= 100.0


def test_wilder_atr_basic():
    atr = WilderATR(3)
    # TR series: 2, 2, 2 -> initial ATR = 2
    out = atr.update(2.0)
    assert out is None or isclose(out, 2.0)
    out = atr.update(2.0)
    assert out is None or isclose(out, 2.0)
    out = atr.update(2.0)
    assert isclose(out or 0.0, 2.0)
    # Next TR keeps ATR around 2 with Wilder smoothing
    out = atr.update(2.0)
    assert isclose(out or 0.0, 2.0, rel_tol=1e-6)


def test_rolling_mean_std():
    rms = RollingMeanStd(3)
    assert rms.update(1.0) is None
    assert rms.update(2.0) is None
    mean, std = rms.update(3.0)
    assert isclose(mean, 2.0)
    assert isclose(std, ((2 / 3)**0.5), rel_tol=1e-6)
