from __future__ import annotations

from qryptify.shared import fees as fees_mod


def test_fee_fetch_falls_back_to_defaults(monkeypatch):
    # Force both fetch paths to fail
    monkeypatch.setattr(fees_mod, "_fetch_fee_bps_httpx", lambda *a, **kw:
                        (_ for _ in ()).throw(RuntimeError("x")))
    monkeypatch.setattr(fees_mod, "_fetch_fee_bps_urllib", lambda *a, **kw:
                        (_ for _ in ()).throw(RuntimeError("y")))
    maker, taker = fees_mod.binance_futures_fee_bps("BTCUSDT",
                                                    timeout_s=0.01,
                                                    ttl_seconds=1)
    assert maker == 2.0
    assert taker == 4.0
