# Qryptify Strategy

Simple, fast bar-close backtesting with two‑sided strategies (long/short), a small engine for ATR sizing, realistic exchange constraints, dynamic fees, and an optimizer that sweeps parameters across pairs and exports results.

## Install

```bash
pip install "psycopg[binary]" pyyaml loguru
```

Python ≥ 3.10 recommended. Data is read from TimescaleDB using the DSN in `qryptify_ingestor/config.yaml`.

Tip: snapshot exchange fees first for realistic results:

```bash
python -m qryptify_ingestor.fees_snapshot --config qryptify_ingestor/config.yaml
```

## Strategies (two‑sided)

- EMA crossover: long on fast>slow cross, short on fast<slow cross (`ema`).
- Bollinger breakout: long on upper breakout, short on lower breakout; exits on midline crosses (`bollinger`).
- RSI mean‑reversion: long on rebound from oversold; short on pullback from overbought; optional EMA filter (`rsi`).

## Backtest CLI

Reads OHLCV from TimescaleDB using the DSN in `qryptify_ingestor/config.yaml`.

Examples

```bash
# EMA 50/200 on 4h (two‑sided)
python -m qryptify_strategy.backtest --pair BTCUSDT/4h --strategy ema --lookback 1000000 \
  --fast 50 --slow 200 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0

# Bollinger 50 × 3.0 on 1h (two‑sided)
python -m qryptify_strategy.backtest --pair BTCUSDT/1h --strategy bollinger --lookback 1000000 \
  --bb-period 50 --bb-mult 3.0 --equity 10000 --risk 0.005 --atr 14 --atr-mult 2.0 --slip-bps 1

# RSI on 15m (two‑sided) with EMA filter
python -m qryptify_strategy.backtest --pair BTCUSDT/15m --strategy rsi --lookback 100000 \
  --rsi-period 14 --rsi-entry 30 --rsi-exit 55 --rsi-ema 200 --equity 10000 --risk 0.005 --atr 14 --atr-mult 3.0 --slip-bps 1
```

Options

- `--pair`: `SYMBOL/interval`
- `--strategy`: `ema`, `bollinger`, `rsi`
- Window: `--lookback` or `--start`/`--end`
- Risk: `--equity`, `--risk`, `--atr`, `--atr-mult`, `--slip-bps`
  - Fees are dynamic by default: the backtester reads `exchange_fees` snapshots from DB and applies the fee in effect at each trade timestamp (taker by default). If no snapshots are present, it falls back to a constant `--fee-bps` (optional).
- EMA: `--fast`, `--slow`
- Bollinger: `--bb-period`, `--bb-mult`
- RSI: `--rsi-period`, `--rsi-entry`, `--rsi-exit`, `--rsi-ema`
- Exchange constraints: `--qty-step`, `--min-qty`, `--min-notional`, `--price-tick`

Execution model

- Signals on close; fills at next open with slippage.
- Stops may gap; gap‑through exits at open, otherwise at stop (both with slippage).
- ATR sizing; orders respect lot step, min notional, and tick size.
- Fees: applied on both entry and exit notionals; shows total fees and average effective bps in the report.
- Flips close at next open then re‑enter opposite (two fees).

## Optimizer

Sweeps parameters across strategies and pairs, ranks by score (`pnl - lam * max_dd`) with an optional drawdown cap, and exports to `reports/`.

Quick start

```bash
# Single pair (BTC 1h), sweep all strategies
python -m qryptify_strategy.optimize --pair BTCUSDT/1h \
  --lookback 1000000 --strategies ema,bollinger,rsi \
  --fast 10,20,30,50 --slow 50,100,200 \
  --risk 0.003,0.005,0.01 --atr-mult 2.0,2.5,3.0 \
  --dd-cap 3000 --lam 0.5 --top-k 10 \
  --out reports/optimizer_results.csv \
  --pareto-dir reports/pareto --md-out reports/optimizer_summary.md

# Multiple pairs; also save the full grid for all pairs
python -m qryptify_strategy.optimize --pairs BTCUSDT/1h,ETHUSDT/4h,BNBUSDT/4h \
  --lookback 1000000 --strategies ema,bollinger,rsi \
  --fast 10,20,30,50 --slow 50,100,200 \
  --risk 0.003,0.005,0.01 --atr-mult 2.0,2.5,3.0 \
  --dd-cap 3000 --lam 0.5 --top-k 10 \
  --out reports/optimizer_results.csv \
  --full-out reports/optimizer_full_grid.csv \
  --pareto-dir reports/pareto --md-out reports/optimizer_summary.md

# Use YAML config (reads pairs/strategies/grids and overrides)
python -m qryptify_strategy.optimize --config qryptify_ingestor/config.yaml \
  --out reports/optimizer_results.csv --pareto-dir reports/pareto --md-out reports/optimizer_summary.md
```

Flags

- `--pair` / `--pairs`: One or many `SYMBOL/interval` targets (comma‑separated)
- `--strategies`: Which strategies to sweep (`ema`, `bollinger`, `rsi`)
- `--fast`, `--slow`: EMA grids (integers; used by `ema`)
- `--risk`: Risk per trade grid (floats)
- `--atr-mult`: ATR stop multiples (floats)
- `--dd-cap`: Max drawdown filter (quote currency), 0 disables
- `--lam`: Score parameter; objective is `pnl - lam * max_dd`
- `--top-k`: How many top rows to print per pair
- `--out`: CSV of best config per pair (default `reports/optimizer_results.csv`)
- `--full-out`: Optional CSV path to dump the entire grid
- `--pareto-dir`: If set, writes per‑pair Pareto frontier CSVs (maximize PnL, minimize DD)
- `--md-out`: Markdown summary path with per‑pair bests, top‑K tables, and a Reproduce command (default `reports/optimizer_summary.md`)
- `--config`: YAML file providing `pairs`, optional `strategies`, grids (`fast`, `slow`, `risk`, `atr_mult`), and overrides (`lookback`, `dd_cap`, `lam`, `top_k`, `out`, `full_out`, `pareto_dir`, `md_out`)

Outputs

- Best‑per‑pair CSV (`--out`): `symbol, interval, strategy, params, risk, atr_mult, pnl, max_dd, trades, equity_end, cagr, avg_fee_bps`
- Full grid CSV (`--full-out`): same columns across all grid rows (`dd` instead of `max_dd`), plus `avg_fee_bps`
- Pareto frontier CSVs (`--pareto-dir`): per pair, non‑dominated points in (PnL↑, DD↓) space, sorted by DD asc
- Markdown summary (`--md-out`): per‑pair section with best config, a top‑K table, and a runnable Reproduce command

## Fees

- Snapshots: Use `python -m qryptify_ingestor.fees_snapshot --config qryptify_ingestor/config.yaml` to snapshot current Binance USDT‑M maker/taker fee bps for all symbols in your config into the `exchange_fees` table.
- Backtests/optimizer automatically load fee snapshots over the test window and apply the appropriate taker fee at each trade timestamp. If no snapshots are found, they fall back to a constant `--fee-bps` value.
- Reports include `avg_fee_bps`, computed as total fees divided by the total entry+exit notional, scaled to bps.

YAML example

```yaml
pairs:
  - BTCUSDT/1h
  - ETHUSDT/4h
strategies: [ema, bollinger, rsi]
fast: [10, 20, 30, 50]
slow: [50, 100, 200]
risk: [0.003, 0.005, 0.01]
atr_mult: [2.0, 2.5, 3.0]
lookback: 1000000
dd_cap: 3000
lam: 0.5
top_k: 10
out: reports/optimizer_results.csv
full_out: reports/optimizer_full_grid.csv
pareto_dir: reports/pareto
md_out: reports/optimizer_summary.md
```

## Code Map

- `qryptify_strategy/backtest.py` — CLI
- `qryptify_strategy/backtester.py` — engine (ATR sizing, stops, fees/slippage)
- `qryptify_strategy/strategies/` — strategy implementations
- `qryptify_strategy/strategy_utils.py` — indicator cores shared by strategies
- `qryptify_strategy/indicators.py` — EMA, WilderRSI, WilderATR, RollingMeanStd, true_range
- `qryptify_strategy/optimize.py` — parameter sweeps, Pareto CSVs, Markdown summary
