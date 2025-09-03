from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import yaml

from qryptify.shared.config import load_cfg_dsn
from qryptify.shared.fees import binance_futures_fee_bps
from qryptify.shared.logging import setup_logging
from qryptify.shared.pairs import parse_pair

from .backtest import build_bars
from .backtester import backtest
from .models import RiskParams
from .strategies.bollinger import BollingerBandStrategy
from .strategies.ema_crossover import EMACrossStrategy
from .strategies.rsi_scalp import RSIScalpStrategy


@dataclass
class Result:
    strategy: str
    params: str
    risk: float
    atr_mult: float
    pnl: float
    dd: float
    trades: int
    cagr: Optional[float]
    equity_end: float
    avg_fee_bps: Optional[float] = None
    # optional per-strategy fields for debugging
    fast: Optional[int] = None
    slow: Optional[int] = None
    bb_period: Optional[int] = None
    bb_mult: Optional[float] = None
    rsi_period: Optional[int] = None
    entry_low: Optional[float] = None
    exit_low: Optional[float] = None
    entry_high: Optional[float] = None
    exit_high: Optional[float] = None


def eval_grid(
    symbol: str,
    interval: str,
    bars,
    strategies: List[str],
    fast_opts: Iterable[int],
    slow_opts: Iterable[int],
    risk_opts: Iterable[float],
    atr_opts: Iterable[float],
    fee_bps_val: float,
) -> List[Result]:
    out: List[Result] = []
    for risk in risk_opts:
        for atr_mult in atr_opts:
            # EMA long/short
            if "ema" in strategies:
                for fast in fast_opts:
                    for slow in slow_opts:
                        if fast >= slow:
                            continue
                        strat = EMACrossStrategy(fast=fast, slow=slow)
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
                                fee_bps=fee_bps_val,
                                fee_lookup=None,
                                slippage_bps=1.0,
                            ),
                        )
                        out.append(
                            Result(
                                strategy="ema",
                                params=f"fast={fast},slow={slow}",
                                risk=risk,
                                atr_mult=atr_mult,
                                pnl=rpt.total_pnl,
                                dd=rpt.max_drawdown,
                                trades=rpt.trades,
                                cagr=rpt.cagr,
                                equity_end=rpt.equity_end,
                                avg_fee_bps=rpt.avg_fee_bps,
                                fast=fast,
                                slow=slow,
                            ))
            # Bollinger long/short
            if "bollinger" in strategies:
                for bb_period in [20, 50]:
                    for bb_mult in [2.0, 2.5, 3.0]:
                        strat = BollingerBandStrategy(period=bb_period, mult=bb_mult)
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
                                fee_bps=fee_bps_val,
                                fee_lookup=None,
                                slippage_bps=1.0,
                            ),
                        )
                        out.append(
                            Result(
                                strategy="bollinger",
                                params=f"period={bb_period},mult={bb_mult}",
                                risk=risk,
                                atr_mult=atr_mult,
                                pnl=rpt.total_pnl,
                                dd=rpt.max_drawdown,
                                trades=rpt.trades,
                                cagr=rpt.cagr,
                                equity_end=rpt.equity_end,
                                avg_fee_bps=rpt.avg_fee_bps,
                                bb_period=bb_period,
                                bb_mult=bb_mult,
                            ))
            # RSI two-sided
            if "rsi" in strategies:
                for rsi_period in [8, 14]:
                    for entry_low in [25.0, 30.0]:
                        for exit_low in [50.0, 55.0]:
                            for ema_filter in [0, 200]:
                                strat = RSIScalpStrategy(
                                    rsi_period=rsi_period,
                                    entry=entry_low,
                                    exit=exit_low,
                                    ema_filter=ema_filter,
                                )
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
                                        fee_bps=fee_bps_val,
                                        fee_lookup=None,
                                        slippage_bps=1.0,
                                    ),
                                )
                                out.append(
                                    Result(
                                        strategy="rsi",
                                        params=
                                        (f"period={rsi_period},eL={entry_low},xL={exit_low},ema={ema_filter}"
                                        ),
                                        risk=risk,
                                        atr_mult=atr_mult,
                                        pnl=rpt.total_pnl,
                                        dd=rpt.max_drawdown,
                                        trades=rpt.trades,
                                        cagr=rpt.cagr,
                                        equity_end=rpt.equity_end,
                                        avg_fee_bps=rpt.avg_fee_bps,
                                        rsi_period=rsi_period,
                                        entry_low=entry_low,
                                        exit_low=exit_low,
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
    scored = sorted(filt, key=lambda r: (r.pnl - lam * r.dd, r.pnl), reverse=True)
    top = scored[0]
    # Return also full ranked list for inspection/export
    return top, scored


def pareto_frontier(results: List[Result]) -> List[Result]:
    """Compute Pareto frontier maximizing pnl and minimizing dd.

    Returns results sorted by dd ascending, keeping only non-dominated points.
    """
    if not results:
        return []
    arr = sorted(results, key=lambda r: (r.dd, -r.pnl))
    frontier: List[Result] = []
    best_pnl = float("-inf")
    for r in arr:
        if r.pnl > best_pnl:
            frontier.append(r)
            best_pnl = r.pnl
    return frontier


def _build_backtest_cmd(symbol: str, interval: str, best: Result, lookback: int) -> str:
    base = [
        "python -m qryptify_strategy.backtest",
        f"--pair {symbol}/{interval}",
        f"--strategy {best.strategy}",
        f"--lookback {lookback}",
        f"--risk {best.risk}",
        "--equity 10000",
        "--atr 14",
        f"--atr-mult {best.atr_mult}",
        "--slip-bps 1",
    ]
    # Pin the fee bps used during optimization for reproducibility
    if best.avg_fee_bps is not None:
        base.append(f"--fee-bps {best.avg_fee_bps}")
    # Strategy-specific args parsed from best.params
    try:
        parts = [p.strip() for p in (best.params or "").split(",") if p.strip()]
        kv = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                kv[k.strip()] = v.strip()
        if best.strategy == "ema":
            if "fast" in kv:
                base.append(f"--fast {kv['fast']}")
            if "slow" in kv:
                base.append(f"--slow {kv['slow']}")
        elif best.strategy == "bollinger":
            if "period" in kv:
                base.append(f"--bb-period {kv['period']}")
            if "mult" in kv:
                base.append(f"--bb-mult {kv['mult']}")
        elif best.strategy == "rsi":
            if "period" in kv:
                base.append(f"--rsi-period {kv['period']}")
            # eL -> rsi-entry, xL -> rsi-exit, ema -> rsi-ema
            if "eL" in kv:
                base.append(f"--rsi-entry {kv['eL']}")
            if "xL" in kv:
                base.append(f"--rsi-exit {kv['xL']}")
            if "ema" in kv:
                base.append(f"--rsi-ema {kv['ema']}")
    except Exception:
        pass
    return " ".join(base)


def main() -> None:
    try:
        setup_logging("INFO")
    except Exception:
        pass
    p = argparse.ArgumentParser(description="Parameter sweep optimizer")
    p.add_argument("--pair", help="SYMBOL/interval, e.g., BTCUSDT/1h (single)")
    p.add_argument("--config", default="", help="YAML with pairs/strategies/grids")
    p.add_argument(
        "--pairs",
        help="Comma-separated list of pairs (SYMBOL/interval). If set, overrides --pair",
    )
    p.add_argument("--lookback", type=int, default=1000000)
    p.add_argument("--strategies",
                   type=str,
                   default="ema,bollinger,rsi",
                   help="Comma-separated strategies to sweep")
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
    p.add_argument("--lam", type=float, default=0.5, help="Score lambda: pnl - lam*dd")
    p.add_argument(
        "--out",
        default="reports/optimizer_results.csv",
        help="Output CSV file with best configs per pair",
    )
    p.add_argument(
        "--full-out",
        default="",
        help="Optional path to write full grid results as CSV (all rows)",
    )
    p.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="How many top rows to print per pair",
    )
    p.add_argument(
        "--pareto-dir",
        default="",
        help="If set, writes Pareto frontier CSV per pair into this directory",
    )
    p.add_argument(
        "--md-out",
        default="reports/optimizer_summary.md",
        help="Markdown summary path with per-pair bests and top-K tables",
    )
    args = p.parse_args()

    # Load optional YAML config
    cfg: dict = {}
    if args.config:
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f) or {}

    # Resolve pairs: CLI > config.pairs
    pair_specs: List[Tuple[str, str]] = []
    if args.pairs:
        for item in args.pairs.split(","):
            item = item.strip()
            if not item:
                continue
            pair_specs.append(parse_pair(item))
    elif args.pair:
        pair_specs.append(parse_pair(args.pair))
    else:
        cfg_pairs = cfg.get("pairs") or []
        if not cfg_pairs:
            raise SystemExit("Provide --pair/--pairs or --config with pairs list")
        for item in cfg_pairs:
            s = None
            if isinstance(item, dict):
                sym = str(item.get("symbol", "")).strip()
                ivl = str(item.get("interval", "")).strip()
                if sym and ivl:
                    s = f"{sym}/{ivl}"
            if s is None:
                s = str(item)
            pair_specs.append(parse_pair(s))

    # Resolve strategies
    if args.strategies:
        strategy_list = [s.strip() for s in args.strategies.split(",") if s]
    else:
        cfg_strats = cfg.get("strategies") or []
        strategy_list = ([str(s).strip() for s in cfg_strats if str(s).strip()]
                         if cfg_strats else ["ema", "bollinger", "rsi"])

    # Grids from CLI with config overrides
    def cfg_list(name: str, arg_vals: List[str]) -> List[str]:
        v = cfg.get(name)
        if v is None:
            v = cfg.get(name.replace("_", "-"))
        if isinstance(v, list):
            return [str(x) for x in v]
        return arg_vals

    fast_opts = [
        int(x) for x in cfg_list("fast", [x for x in args.fast.split(",") if x])
    ]
    slow_opts = [
        int(x) for x in cfg_list("slow", [x for x in args.slow.split(",") if x])
    ]
    risk_opts = [
        float(x) for x in cfg_list("risk", [x for x in args.risk.split(",") if x])
    ]
    atr_opts = [
        float(x) for x in cfg_list(
            "atr_mult", [x for x in getattr(args, "atr_mult").split(",") if x])
    ]

    # Scalars
    lookback = int(cfg.get("lookback", args.lookback))
    dd_cap = cfg.get("dd_cap", args.dd_cap)
    dd_cap = None if dd_cap and float(dd_cap) <= 0 else float(dd_cap)
    lam = float(cfg.get("lam", args.lam))
    top_k = int(cfg.get("top_k", args.top_k))

    # Outputs
    out_path = cfg.get("out", args.out)
    full_out = cfg.get("full_out", args.full_out)
    pareto_dir = cfg.get("pareto_dir", args.pareto_dir)
    md_out = cfg.get("md_out", args.md_out)

    from qryptify.data.timescale import TimescaleRepo
    dsn = load_cfg_dsn()

    import csv
    import os
    rows_out: List[dict] = []
    md_lines: List[str] = ["# Optimizer Summary\n"]
    # Keep all results per pair to avoid recomputing for --full-out later
    all_results: List[Tuple[str, str, List[Result]]] = []

    for symbol, interval in pair_specs:
        repo = TimescaleRepo(dsn)
        repo.connect()
        try:
            rows = repo.fetch_latest_n(symbol, interval, lookback)
        finally:
            repo.close()
        bars = build_bars(rows)

        # Resolve fixed taker fee bps for this symbol via API (fallback 4.0 bps)
        try:
            _, taker_bps = binance_futures_fee_bps(symbol)
            fee_bps_val = float(taker_bps)
        except Exception:
            fee_bps_val = 4.0

        try:
            results = eval_grid(symbol, interval, bars, strategy_list, fast_opts,
                                slow_opts, risk_opts, atr_opts, fee_bps_val)
        except Exception as e:
            print(f"\nSkipping {symbol} {interval}: {e}")
            continue
        if not results:
            print(f"\nNo results for {symbol} {interval} (check data or grids)")
            continue
        # Save for potential full-grid export without recomputation
        all_results.append((symbol, interval, results))
        best, ranked = choose_best(results, dd_cap, lam)

        print(f"\nSweep done for {symbol} {interval}")
        print("Top by score (pnl - lam*dd):")
        for r in ranked[:max(1, top_k)]:
            print(
                f"  strat={r.strategy} params={r.params} risk={r.risk} atr={r.atr_mult} "
                f"pnl={r.pnl:.2f} dd={r.dd:.0f} trades={r.trades} eq={r.equity_end:.2f} cagr={(r.cagr or 0.0):.2%} avg_fee_bps={(r.avg_fee_bps or 0.0):.2f}"
            )
        print("Recommended:")
        print(
            f"  strat={best.strategy} params={best.params} risk={best.risk} atr={best.atr_mult} "
            f"pnl={best.pnl:.2f} dd={best.dd:.0f} trades={best.trades} eq={best.equity_end:.2f} cagr={(best.cagr or 0.0):.2%} avg_fee_bps={(best.avg_fee_bps or 0.0):.2f}"
        )

        # Markdown section for this pair
        md_lines.append(f"\n## {symbol} {interval}\n")
        md_lines.append(
            f"Best (score=pnl-lam*dd): {best.strategy} | {best.params} | risk={best.risk} | atr={best.atr_mult} | pnl={best.pnl:.2f} | dd={best.dd:.0f} | trades={best.trades} | eq={best.equity_end:.2f} | cagr={(best.cagr or 0.0):.2%} | avg_fee_bps={(best.avg_fee_bps or 0.0):.2f}\n"
        )
        # Reproduce command
        cmd = _build_backtest_cmd(symbol, interval, best, args.lookback)
        md_lines.append("Reproduce:\n")
        md_lines.append("```bash")
        md_lines.append(cmd)
        md_lines.append("```")
        md_lines.append("\nTop Results\n")
        md_lines.append(
            "| Strategy | Params | Risk | ATR | PnL | DD | Trades | Equity | CAGR | Fee(bps) |\n|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
        )
        for r in ranked[:max(1, top_k)]:
            md_lines.append(
                f"| {r.strategy} | {r.params} | {r.risk} | {r.atr_mult} | {r.pnl:.2f} | {r.dd:.0f} | {r.trades} | {r.equity_end:.2f} | {(r.cagr or 0.0):.2%} | {(r.avg_fee_bps or 0.0):.2f} |"
            )

        rows_out.append({
            "symbol": symbol,
            "interval": interval,
            "strategy": best.strategy,
            "params": best.params,
            "risk": best.risk,
            "atr_mult": best.atr_mult,
            "pnl": round(best.pnl, 2),
            "max_dd": round(best.dd, 2),
            "trades": best.trades,
            "equity_end": round(best.equity_end, 2),
            "cagr": round((best.cagr or 0.0) * 100, 2),
            "avg_fee_bps": round((best.avg_fee_bps or 0.0), 4),
        })

        # Pareto frontier per pair
        if pareto_dir:
            outdir = Path(pareto_dir)
            outdir.mkdir(parents=True, exist_ok=True)
            fname = f"pareto_{symbol}_{interval.replace('/', '_')}.csv"
            ppath = outdir / fname
            frontier = pareto_frontier(results)
            with ppath.open("w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "strategy",
                        "params",
                        "risk",
                        "atr_mult",
                        "pnl",
                        "dd",
                        "trades",
                        "equity_end",
                        "cagr",
                        "avg_fee_bps",
                    ],
                )
                writer.writeheader()
                for r in frontier:
                    writer.writerow({
                        "strategy": r.strategy,
                        "params": r.params,
                        "risk": r.risk,
                        "atr_mult": r.atr_mult,
                        "pnl": round(r.pnl, 2),
                        "dd": round(r.dd, 2),
                        "trades": r.trades,
                        "equity_end": round(r.equity_end, 2),
                        "cagr": round((r.cagr or 0.0) * 100, 2),
                        "avg_fee_bps": round((r.avg_fee_bps or 0.0), 4),
                    })
            print(f"Saved Pareto frontier to {ppath}")

    # Write CSV
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "symbol",
                "interval",
                "strategy",
                "params",
                "risk",
                "atr_mult",
                "pnl",
                "max_dd",
                "trades",
                "equity_end",
                "cagr",
                "avg_fee_bps",
            ],
        )
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"\nSaved results to {out_path}")

    # Optional full grid CSV
    if full_out:
        os.makedirs(os.path.dirname(full_out) or ".", exist_ok=True)
        with open(full_out, "w", newline="") as f:
            fieldnames = [
                "symbol",
                "interval",
                "strategy",
                "params",
                "risk",
                "atr_mult",
                "pnl",
                "dd",
                "trades",
                "equity_end",
                "cagr",
                "avg_fee_bps",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for symbol, interval, res in all_results:
                for r in res:
                    writer.writerow({
                        "symbol": symbol,
                        "interval": interval,
                        "strategy": r.strategy,
                        "params": r.params,
                        "risk": r.risk,
                        "atr_mult": r.atr_mult,
                        "pnl": round(r.pnl, 2),
                        "dd": round(r.dd, 2),
                        "trades": r.trades,
                        "equity_end": round(r.equity_end, 2),
                        "cagr": round((r.cagr or 0.0) * 100, 2),
                        "avg_fee_bps": round((r.avg_fee_bps or 0.0), 4),
                    })
        print(f"Saved full grid to {full_out}")

    # Write Markdown summary
    md_path = Path(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(md_lines) + "\n")
    print(f"Saved summary to {md_path}")


if __name__ == "__main__":
    main()
