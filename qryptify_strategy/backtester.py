from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from .indicators import true_range
from .indicators import WilderATR
from .models import BacktestReport
from .models import Bar
from .models import RiskParams
from .models import Signal
from .models import Trade
from .strategy_base import Strategy


@dataclass
class BacktestState:
    equity: float
    position_qty: float = 0.0
    entry_price: Optional[float] = None
    entry_ts: Optional[datetime] = None
    stop_price: Optional[float] = None
    open_fees: float = 0.0
    max_equity: float = 0.0


def _apply_fees(notional: float, fee_bps: float) -> float:
    return notional * (fee_bps / 10_000.0)


def _price_with_slippage(price: float, bps: float, side: str) -> float:
    adj = price * (bps / 10_000.0)
    if side.upper() == "BUY":
        return price + adj
    else:
        return price - adj


def _floor_to_step(value: float, step: float) -> float:
    if step and step > 0:
        n = int(value / step)
        return max(n * step, 0.0)
    return value


def _floor_price_tick(price: float, tick: float) -> float:
    return _floor_to_step(price, tick)


def backtest(
    symbol: str,
    interval: str,
    bars: List[Bar],
    strategy: Strategy,
    risk: RiskParams,
) -> Tuple[BacktestReport, List[Trade]]:
    if not bars:
        raise ValueError("No bars provided")

    state = BacktestState(equity=risk.start_equity,
                          max_equity=risk.start_equity)
    atr_calc = WilderATR(risk.atr_period)
    trades: List[Trade] = []
    prev_close: Optional[float] = None

    strategy.on_start()
    equity_series: List[float] = []

    for i in range(len(bars)):
        bar = bars[i]
        tr = true_range(bar.high, bar.low, prev_close)
        atr = atr_calc.update(tr)

        sig: Optional[Signal] = strategy.on_bar(i, bar)

        exit_reason: Optional[str] = None
        exit_price: Optional[float] = None
        if state.position_qty > 0 and state.stop_price is not None:
            stop_px = state.stop_price
            if bar.open <= stop_px:
                exit_reason = "stop_gap"
                exit_price = _price_with_slippage(bar.open, risk.slippage_bps,
                                                  "SELL")
            elif bar.low <= stop_px:
                exit_reason = "stop"
                exit_price = _price_with_slippage(stop_px, risk.slippage_bps,
                                                  "SELL")

        next_open_price = bars[i + 1].open if (i + 1) < len(bars) else None

        if exit_reason and state.position_qty > 0:
            qty = state.position_qty
            exit_p = exit_price or bar.close
            fees = _apply_fees(qty * exit_p, risk.fee_bps)
            pnl = (
                exit_p -
                (state.entry_price or exit_p)) * qty - fees - state.open_fees
            state.equity += pnl
            trades.append(
                Trade(
                    entry_ts=state.entry_ts
                    or (bars[i - 1].ts if i > 0 else bar.ts),
                    exit_ts=bar.ts,
                    entry_price=state.entry_price or 0.0,
                    exit_price=exit_p,
                    qty=qty,
                    pnl=pnl,
                    fees=fees + state.open_fees,
                    reason=exit_reason,
                ))
            state.position_qty = 0.0
            state.entry_price = None
            state.entry_ts = None
            state.stop_price = None
            state.open_fees = 0.0

        if next_open_price is not None and sig is not None:
            if sig.target == 0 and state.position_qty > 0:
                px = _price_with_slippage(next_open_price, risk.slippage_bps,
                                          "SELL")
                qty = state.position_qty
                fees = _apply_fees(qty * px, risk.fee_bps)
                pnl = (
                    px -
                    (state.entry_price or px)) * qty - fees - state.open_fees
                state.equity += pnl
                trades.append(
                    Trade(
                        entry_ts=state.entry_ts or bar.ts,
                        exit_ts=bars[i + 1].ts,
                        entry_price=state.entry_price or 0.0,
                        exit_price=px,
                        qty=qty,
                        pnl=pnl,
                        fees=fees + state.open_fees,
                        reason=sig.reason or "signal_exit",
                    ))
                state.position_qty = 0.0
                state.entry_price = None
                state.entry_ts = None
                state.stop_price = None
                state.open_fees = 0.0
            elif sig.target == 1 and state.position_qty <= 0 and atr is not None:
                px = _price_with_slippage(next_open_price, risk.slippage_bps,
                                          "BUY")
                risk_cash = state.equity * risk.risk_per_trade
                stop_dist = atr * risk.atr_mult_stop
                if stop_dist <= 0:
                    prev_close = bar.close
                    continue
                qty = max(risk_cash / stop_dist, 0.0)
                qty = _floor_to_step(qty, getattr(risk, "qty_step", 0.0))
                min_qty = getattr(risk, "min_qty", 0.0) or 0.0
                min_notional = getattr(risk, "min_notional", 0.0) or 0.0
                if qty <= 0 or qty < min_qty or (qty * px) < min_notional:
                    prev_close = bar.close
                    continue
                open_fees = _apply_fees(qty * px, risk.fee_bps)
                state.position_qty = qty
                state.entry_price = px
                state.entry_ts = bars[i + 1].ts
                state.open_fees = open_fees
                stop_px = max(px - stop_dist, 0.0)
                stop_px = _floor_price_tick(stop_px,
                                            getattr(risk, "price_tick", 0.0))
                state.stop_price = stop_px

        mtm = state.equity
        if state.position_qty > 0 and state.entry_price is not None:
            mtm += (bar.close - state.entry_price) * state.position_qty
        if mtm > state.max_equity:
            state.max_equity = mtm
        equity_series.append(mtm)

        prev_close = bar.close

    if state.position_qty > 0 and bars:
        last_bar = bars[-1]
        px = _price_with_slippage(last_bar.close, risk.slippage_bps, "SELL")
        fees = _apply_fees(state.position_qty * px, risk.fee_bps)
        pnl = (px - (state.entry_price
                     or px)) * state.position_qty - fees - state.open_fees
        state.equity += pnl
        trades.append(
            Trade(
                entry_ts=state.entry_ts or bars[-1].ts,
                exit_ts=last_bar.ts,
                entry_price=state.entry_price or 0.0,
                exit_price=px,
                qty=state.position_qty,
                pnl=pnl,
                fees=fees + state.open_fees,
                reason="final_close",
            ))

    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]
    win_rate = len(wins) / len(trades) if trades else 0.0
    avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0.0
    avg_loss = sum(t.pnl for t in losses) / len(losses) if losses else 0.0
    total_pnl = sum(t.pnl for t in trades)
    total_fees = sum(t.fees for t in trades)

    span_sec = max((bars[-1].ts - bars[0].ts).total_seconds(), 1.0)
    years = span_sec / (365.25 * 24 * 3600)
    cagr = (state.equity /
            risk.start_equity)**(1 / years) - 1 if years > 0 else None

    peak = equity_series[0] if equity_series else risk.start_equity
    max_dd = 0.0
    for eq in equity_series:
        if eq > peak:
            peak = eq
        dd = peak - eq
        if dd > max_dd:
            max_dd = dd

    rpt = BacktestReport(
        symbol=symbol,
        interval=interval,
        bars=len(bars),
        trades=len(trades),
        total_pnl=total_pnl,
        total_fees=total_fees,
        equity_end=state.equity,
        max_drawdown=max_dd,
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        cagr=cagr,
    )
    strategy.on_finish()
    return rpt, trades
