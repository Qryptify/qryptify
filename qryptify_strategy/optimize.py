from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .backtest import _parse_pair
from .backtest import build_bars
from .backtest import load_cfg_dsn
from .backtester import backtest
from .models import RiskParams
from .strategies.ema_crossover_ls import EMACrossLongShortStrategy


@dataclass
class Result:
    fast: int
    slow: int
    risk: float
    atr_mult: float
    pnl: float
    dd: float
    trades: int
    cagr: float | None
    equity_end: float


def eval_grid(
    symbol: str,
    interval: str,
    bars,
    fast_opts: Iterable[int],
    slow_opts: Iterable[int],
    risk_opts: Iterable[float],
    atr_opts: Iterable[float],
) -> List[Result]:
    out: List[Result] = []
    for fast in fast_opts:
        for slow in slow_opts:
            if fast >= slow:
                continue
            for risk in risk_opts:
                for atr_mult in atr_opts:
                    strat = EMACrossLongShortStrategy(fast=fast, slow=slow)
                    rpt, _ = backtest(
                        symbol,
                        interval,
                        bars,
                        strat,
                        RiskParams(
                            start_equity=10_000.0,
                            risk_per_trade=risk,
                            atr_period=14,
                            atr_mult_stop=atr_mult,
                            fee_bps=4.0,
                            slippage_bps=1.0,
                        ),
                    )
                    out.append(
                        Result(
                            fast=fast,
                            slow=slow,
                            risk=risk,
                            atr_mult=atr_mult,
                            pnl=rpt.total_pnl,
                            dd=rpt.max_drawdown,
                            trades=rpt.trades,
                            cagr=rpt.cagr,
                            equity_end=rpt.equity_end,
                        ))
    return out


def choose_best(results: List[Result], dd_cap: float | None,
                lam: float) -> Tuple[Result, List[Result]]:
    # Filter by drawdown cap if provided
    filt = [r for r in results if dd_cap is None or r.dd <= dd_cap]
    if not filt:
        # If nothing passes, pick best score without cap
        filt = results
    # Score: pnl - lam * dd
    scored = sorted(filt,
                    key=lambda r: (r.pnl - lam * r.dd, r.pnl),
                    reverse=True)
    top = scored[0]
    # Return also top 10 frontier for inspection
    return top, scored[:10]


def main() -> None:
    p = argparse.ArgumentParser(description="Parameter sweep optimizer")
    p.add_argument("--pair", help="SYMBOL/interval, e.g., BTCUSDT/1h (single)")
    p.add_argument(
        "--pairs",
        help=
        "Comma-separated list of pairs (SYMBOL/interval). If set, overrides --pair",
    )
    p.add_argument("--lookback", type=int, default=32132)
    p.add_argument("--fast",
                   type=str,
                   default="10,20,30,50",
                   help="Comma-separated fast EMA options")
    p.add_argument("--slow",
                   type=str,
                   default="50,100,200",
                   help="Comma-separated slow EMA options")
    p.add_argument("--risk",
                   type=str,
                   default="0.003,0.005,0.01",
                   help="Comma-separated risk per trade options")
    p.add_argument("--atr-mult",
                   type=str,
                   default="2.0,2.5,3.0",
                   help="Comma-separated ATR stop multiples")
    p.add_argument("--dd-cap",
                   type=float,
                   default=3000.0,
                   help="Max drawdown cap (quote currency), 0 to disable")
    p.add_argument("--lam",
                   type=float,
                   default=0.5,
                   help="Score lambda: pnl - lam*dd")
    p.add_argument(
        "--out",
        default="optimizer_results.csv",
        help="Output CSV file with best configs per pair",
    )
    args = p.parse_args()

    pair_specs: List[Tuple[str, str]] = []
    if args.pairs:
        for item in args.pairs.split(","):
            item = item.strip()
            if not item:
                continue
            pair_specs.append(_parse_pair(item))
    elif args.pair:
        pair_specs.append(_parse_pair(args.pair))
    else:
        raise SystemExit("Provide --pair or --pairs")

    fast_opts = [int(x) for x in args.fast.split(",") if x]
    slow_opts = [int(x) for x in args.slow.split(",") if x]
    risk_opts = [float(x) for x in args.risk.split(",") if x]
    # argparse converts dashes to underscores
    atr_opts = [float(x) for x in getattr(args, "atr_mult").split(",") if x]
    dd_cap = None if args.dd_cap and args.dd_cap <= 0 else args.dd_cap

    from qryptify_ingestor.timescale_repo import TimescaleRepo  # late import
    dsn = load_cfg_dsn()

    import csv
    rows_out: List[dict] = []

    for symbol, interval in pair_specs:
        repo = TimescaleRepo(dsn)
        repo.connect()
        try:
            rows = repo.fetch_latest_n(symbol, interval, args.lookback)
        finally:
            repo.close()
        bars = build_bars(rows)

        results = eval_grid(symbol, interval, bars, fast_opts, slow_opts,
                            risk_opts, atr_opts)
        best, top10 = choose_best(results, dd_cap, args.lam)

        print(f"\nSweep done for {symbol} {interval}")
        print("Top by score (pnl - lam*dd):")
        for r in top10:
            print(
                f"  fast={r.fast} slow={r.slow} risk={r.risk} atr={r.atr_mult} pnl={r.pnl:.2f} dd={r.dd:.0f} trades={r.trades} eq={r.equity_end:.2f} cagr={(r.cagr or 0.0):.2%}"
            )
        print("Recommended:")
        print(
            f"  fast={best.fast} slow={best.slow} risk={best.risk} atr={best.atr_mult} pnl={best.pnl:.2f} dd={best.dd:.0f} trades={best.trades} eq={best.equity_end:.2f} cagr={(best.cagr or 0.0):.2%}"
        )

        rows_out.append({
            "symbol": symbol,
            "interval": interval,
            "fast": best.fast,
            "slow": best.slow,
            "risk": best.risk,
            "atr_mult": best.atr_mult,
            "pnl": round(best.pnl, 2),
            "max_dd": round(best.dd, 2),
            "trades": best.trades,
            "equity_end": round(best.equity_end, 2),
            "cagr": round((best.cagr or 0.0) * 100, 2),
        })

    # Write CSV
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "symbol",
                "interval",
                "fast",
                "slow",
                "risk",
                "atr_mult",
                "pnl",
                "max_dd",
                "trades",
                "equity_end",
                "cagr",
            ],
        )
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"\nSaved results to {args.out}")


if __name__ == "__main__":
    main()
