from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional


@dataclass
class Bar:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Signal:
    # Target exposure: -1 short, 0 flat, +1 long
    target: int
    reason: str = ""


@dataclass
class RiskParams:
    start_equity: float = 10_000.0
    risk_per_trade: float = 0.01  # 1% of equity
    atr_period: int = 14
    atr_mult_stop: float = 2.0
    fee_bps: float = 4.0  # 4 bps (0.04%)
    slippage_bps: float = 1.0  # 1 bps simulated
    # Optional exchange-like constraints / rounding for live realism
    qty_step: float = 0.0  # round qty down to this step
    min_qty: float = 0.0  # enforce minimum order quantity
    min_notional: float = 0.0  # enforce minimum notional (qty*price)
    price_tick: float = 0.0  # round stop/limit prices to this tick
    # Optional ATR trailing stop multiplier (>0 enables trailing)
    atr_mult_trail: float = 0.0
    # Optional MFE trigger before trailing activates (in ATRs)
    atr_trail_trigger_mult: float = 0.0
    # Optional dynamic fee lookup: function(ts) -> fee_bps; overrides fee_bps if set
    fee_lookup: Optional[Callable[[datetime], float]] = None


@dataclass
class Trade:
    entry_ts: datetime
    exit_ts: datetime
    entry_price: float
    exit_price: float
    qty: float
    pnl: float
    fees: float
    reason: str


@dataclass
class BacktestReport:
    symbol: str
    interval: str
    bars: int
    trades: int
    total_pnl: float
    total_fees: float
    equity_end: float
    max_drawdown: float
    win_rate: float
    avg_win: float
    avg_loss: float
    cagr: Optional[float]
    avg_fee_bps: float = 0.0
    fee_model: str = "fixed_bps"
