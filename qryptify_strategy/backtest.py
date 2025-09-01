from __future__ import annotations

import argparse
from datetime import datetime
from typing import List

from .backtester import backtest
from .models import Bar
from .models import RiskParams
from .strategies.bollinger import BollingerBandStrategy
from .strategies.ema_crossover import EMACrossStrategy
from .strategies.rsi_scalp import RSIScalpStrategy


def _parse_pair(pair: str) -> tuple[str, str]:
    if "/" in pair:
        s, i = pair.split("/", 1)
    elif "-" in pair:
        s, i = pair.split("-", 1)
    else:
        raise ValueError("pair must be SYMBOL/interval or SYMBOL-interval")
    return s.upper(), i


def load_cfg_dsn(path: str = "qryptify_ingestor/config.yaml") -> str:
    # Local import so --help works without pyyaml installed
    import yaml  # type: ignore
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg["db"]["dsn"]


def build_bars(rows: List[dict]) -> List[Bar]:
    out: List[Bar] = []
    for r in rows:
        out.append(
            Bar(
                ts=r["ts"],
                open=float(r["open"]),
                high=float(r["high"]),
                low=float(r["low"]),
                close=float(r["close"]),
                volume=float(r["volume"]),
            ))
    return out


def main() -> None:
    p = argparse.ArgumentParser(
        description="Backtest strategies on stored OHLCV")
    p.add_argument("--pair",
                   help="SYMBOL/interval like BTCUSDT/4h",
                   required=True)
    p.add_argument(
        "--strategy",
        choices=["ema", "bollinger", "boll", "bb", "rsi", "rsi_mr"],
        default="ema",
        help="Strategy: ema | bollinger | rsi",
    )
    p.add_argument("--lookback",
                   type=int,
                   help="fetch latest N bars",
                   default=2000)
    p.add_argument("--start", help="ISO start datetime (UTC)")
    p.add_argument("--end", help="ISO end datetime (UTC)")
    # EMA params
    p.add_argument("--fast",
                   type=int,
                   default=50,
                   help="EMA fast period (ema)")
    p.add_argument("--slow",
                   type=int,
                   default=200,
                   help="EMA slow period (ema)")
    # Bollinger params
    p.add_argument("--bb-period",
                   type=int,
                   default=20,
                   help="Bollinger lookback period (bollinger)")
    p.add_argument("--bb-mult",
                   type=float,
                   default=2.0,
                   help="Bollinger std-dev multiplier (bollinger)")
    # RSI scalping params
    p.add_argument("--rsi-period",
                   type=int,
                   default=14,
                   help="RSI period (rsi)")
    p.add_argument("--rsi-entry",
                   type=float,
                   default=30.0,
                   help="RSI entry threshold, cross up (rsi)")
    p.add_argument("--rsi-exit",
                   type=float,
                   default=55.0,
                   help="RSI exit threshold, cross up (rsi)")
    p.add_argument("--rsi-ema",
                   type=int,
                   default=200,
                   help="EMA filter period, 0 to disable (rsi)")
    p.add_argument("--equity", type=float, default=10_000.0)
    p.add_argument("--risk", type=float, default=0.01)
    p.add_argument("--atr", type=int, default=14)
    p.add_argument("--atr-mult", type=float, default=2.0)
    p.add_argument("--fee-bps", type=float, default=4.0)
    p.add_argument("--slip-bps", type=float, default=1.0)
    # Optional exchange constraints (improve live reproducibility)
    p.add_argument("--qty-step",
                   type=float,
                   default=0.0,
                   help="Round quantity down to this step (0 to ignore)")
    p.add_argument("--min-qty",
                   type=float,
                   default=0.0,
                   help="Minimum order quantity (0 to ignore)")
    p.add_argument(
        "--min-notional",
        type=float,
        default=0.0,
        help="Minimum order notional in quote currency (0 to ignore)")
    p.add_argument("--price-tick",
                   type=float,
                   default=0.0,
                   help="Price tick size for stop rounding (0 to ignore)")
    args = p.parse_args()

    symbol, interval = _parse_pair(args.pair)

    # Local import so --help works without loguru/psycopg until run
    from qryptify_ingestor.timescale_repo import TimescaleRepo  # type: ignore
    dsn = load_cfg_dsn()
    repo = TimescaleRepo(dsn)
    repo.connect()
    try:
        if args.start or args.end:
            start = (datetime.fromisoformat(args.start.replace("Z", "+00:00"))
                     if args.start else None)
            end = (datetime.fromisoformat(args.end.replace("Z", "+00:00"))
                   if args.end else None)
            rows = repo.fetch_ohlcv(symbol, interval, start=start, end=end)
        else:
            rows = repo.fetch_latest_n(symbol, interval, args.lookback)

        print(f"Fetched {len(rows)} bars for {symbol}/{interval}")
        bars = build_bars(rows)
        # Select strategy
        strat_key = args.strategy
        if strat_key in ("boll", "bb"):
            strat_key = "bollinger"
        if strat_key == "rsi_mr":
            strat_key = "rsi"

        if strat_key == "ema":
            strategy = EMACrossStrategy(fast=args.fast, slow=args.slow)
        elif strat_key == "bollinger":
            strategy = BollingerBandStrategy(period=args.bb_period,
                                             mult=args.bb_mult)
        elif strat_key == "rsi":
            strategy = RSIScalpStrategy(
                rsi_period=args.rsi_period,
                entry=args.rsi_entry,
                exit=args.rsi_exit,
                ema_filter=args.rsi_ema,
            )
        else:
            raise ValueError(f"Unknown strategy: {args.strategy}")
        risk = RiskParams(
            start_equity=args.equity,
            risk_per_trade=args.risk,
            atr_period=args.atr,
            atr_mult_stop=args.atr_mult,
            fee_bps=args.fee_bps,
            slippage_bps=args.slip_bps,
            qty_step=args.qty_step,
            min_qty=args.min_qty,
            min_notional=args.min_notional,
            price_tick=args.price_tick,
        )

        report, trades = backtest(symbol, interval, bars, strategy, risk)

        # Print summary
        print("Summary")
        print(f"  Pair:       {report.symbol}/{report.interval}")
        print(f"  Bars:       {report.bars}")
        print(f"  Trades:     {report.trades}")
        print(f"  Win rate:   {report.win_rate:.1%}")
        print(f"  Avg win:    {report.avg_win:.2f}")
        print(f"  Avg loss:   {report.avg_loss:.2f}")
        print(f"  Fees:       {report.total_fees:.2f}")
        print(f"  PnL:        {report.total_pnl:.2f}")
        print(f"  Equity end: {report.equity_end:.2f}")
        if report.cagr is not None:
            print(f"  CAGR:       {report.cagr:.2%}")
        print(f"  Max DD:     {report.max_drawdown:.2f}")

        # Show last few trades
        last = trades[-5:]
        if last:
            print("\nLast trades")
            for t in last:
                print(
                    f"  {t.entry_ts.isoformat()} -> {t.exit_ts.isoformat()} | qty={t.qty:.6f} entry={t.entry_price:.2f} exit={t.exit_price:.2f} pnl={t.pnl:.2f} reason={t.reason}"
                )
    finally:
        repo.close()


if __name__ == "__main__":
    main()
