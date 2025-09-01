# Qryptify Strategy

Bar-close strategy layer with a simple backtester.

## Install

```bash
pip install "psycopg[binary]" pyyaml
```

## Backtest CLI

Reads DSN from `qryptify_ingestor/config.yaml` and OHLCV from TimescaleDB.

Examples:

```bash
# EMA 50/200 on 4h
python -m qryptify_strategy.backtest --pair BTCUSDT/4h --strategy ema --lookback 1000000 \
  --fast 50 --slow 200 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0

# Two-sided EMA (long/short) on 1h
python -m qryptify_strategy.backtest --pair BTCUSDT/1h --strategy ema --lookback 1000000 --fast 50 --slow 200 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0 --fee-bps 4 --slip-bps 1

# Two-sided Bollinger on 1h
python -m qryptify_strategy.backtest --pair BTCUSDT/1h --strategy bollinger --bb-period 50 --bb-mult 3.0 \
  --equity 10000 --risk 0.005 --atr 14 --atr-mult 2.0 --fee-bps 4 --slip-bps 1 --lookback 1000000

# RSI scalping on 15m
python -m qryptify_strategy.backtest --pair BTCUSDT/15m --strategy rsi \
  --rsi-period 8 --rsi-entry 28 --rsi-exit 58 --rsi-ema 50 --
```

Options:

- `--pair`: `SYMBOL/interval`
- `--strategy`: `ema`, `bollinger`, `rsi` (all two-sided)
- Window: `--lookback` or `--start`/`--end`
- Risk: `--equity`, `--risk`, `--atr`, `--atr-mult`, `--fee-bps`, `--slip-bps`
- EMA: `--fast`, `--slow`
- Bollinger: `--bb-period`, `--bb-mult`
- RSI: `--rsi-period`, `--rsi-entry`, `--rsi-exit`, `--rsi-ema`
- Exchange constraints: `--qty-step`, `--min-qty`, `--min-notional`, `--price-tick`

Execution model:

- Signals on close; fills at next open with slippage.
- Gap-through stops exit at open; otherwise at stop, with slippage.
- ATR sizing; orders respect lot step/min notional/tick.

## Strategies

- EMA crossover (two-sided)
- Bollinger breakout (two-sided)
- RSI mean-reversion (two-sided) with optional EMA filter

## Code Map

- `qryptify_strategy/backtest.py` — CLI
- `qryptify_strategy/backtester.py` — engine (ATR sizing, stops, fees/slippage)
- `qryptify_strategy/strategies/` — strategy implementations
- `qryptify_strategy/indicators.py` — EMA, WilderRSI, WilderATR, RollingMeanStd, true_range

## Optimizer

Sweep parameters across strategies and pairs, pick best by score, and export CSVs to `reports/`.

Quick start:

```bash
# Single pair (BTC 1h), sweep all strategies
python -m qryptify_strategy.optimize --pair BTCUSDT/1h \
  --lookback 1000000 --strategies ema,bollinger,rsi \
  --fast 10,20,30,50 --slow 50,100,200 \
  --risk 0.003,0.005,0.01 --atr-mult 2.0,2.5,3.0 \
  --dd-cap 3000 --lam 0.5 --top-k 10 \
  --out reports/optimizer_results.csv

# Multiple pairs; also save the full grid
python -m qryptify_strategy.optimize --pairs BTCUSDT/1h,ETHUSDT/4h,BNBUSDT/4h \
  --lookback 1000000 --strategies ema,bollinger,rsi \
  --fast 10,20,30,50 --slow 50,100,200 \
  --risk 0.003,0.005,0.01 --atr-mult 2.0,2.5,3.0 \
  --dd-cap 3000 --lam 0.5 --top-k 10 \
  --out reports/optimizer_results.csv --full-out reports/optimizer_full_grid.csv

# Single pair (BTC 1h), sweep all strategies
python -m qryptify_strategy.optimize --pair BTCUSDT/1h \
  --lookback 1000000 --strategies ema,bollinger,rsi \
  --fast 10,20,30,50 --slow 50,100,200 \
  --risk 0.003,0.005,0.01 --atr-mult 2.0,2.5,3.0 \
  --dd-cap 3000 --lam 0.5 --top-k 10 \
  --out reports/optimizer_results.csv \
  --pareto-dir reports/pareto --md-out reports/optimizer_summary.md
```

Flags:

- `--pair` / `--pairs`: One or many `SYMBOL/interval` targets (comma‑separated).
- `--strategies`: Which strategies to sweep (`ema`, `bollinger`, `rsi`).
- `--fast`, `--slow`: EMA grids (comma‑separated integers; used by `ema`).
- `--risk`: Risk per trade grid (floats).
- `--atr-mult`: ATR stop multiples (floats).
- `--dd-cap`: Max drawdown filter (quote currency), 0 disables.
- `--lam`: Score parameter; objective is `pnl - lam * max_dd`.
- `--top-k`: How many top rows to print per pair.
- `--out`: CSV of best config per pair (default `reports/optimizer_results.csv`).
- `--full-out`: Optional CSV path to dump the entire grid.
- `--pareto-dir`: If set, writes per‑pair Pareto frontier CSVs (maximize PnL, minimize DD).
- `--md-out`: Markdown summary path with per‑pair bests and top‑K tables (default `reports/optimizer_summary.md`).

Notes:

- DSN is read from `qryptify_ingestor/config.yaml`. Ensure TimescaleDB has data for your pairs/intervals.
- The report CSV columns: symbol, interval, strategy, params, risk, atr_mult, pnl, max_dd, trades, equity_end, cagr.
- Pareto frontier CSVs contain non‑dominated points in (PnL↑, DD↓) space, sorted by DD asc.
