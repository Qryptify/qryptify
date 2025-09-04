# Qryptify

Binance Futures data + strategy playground:

- Ingestor: backfills and streams closed klines into TimescaleDB with idempotent writes and resume pointers.
- Strategy: simple, fast bar-close backtesting (two‑sided: long/short) with ATR sizing, exchange-like constraints, API‑based fees by default, and a parameter optimizer.

See component READMEs for focused guides:

- `qryptify_ingestor/README.md`
- `qryptify_strategy/README.md`

## Quick Start

1. Start TimescaleDB and auto‑init schema:

```bash
docker compose up -d
```

2. Install the package. For development (lint/type/test), use the dev extras:

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

3. Configure pairs and DSN in `qryptify_ingestor/config.yaml`, then ingest and verify:

```bash
qryptify-ingest   # or: python main.py
./verify_ingestion.sh
```

Pair formats supported:

- `SYMBOL/interval` (e.g., `BTCUSDT/1h`)
- `SYMBOL-interval` (e.g., `ETHUSDT-4h`)
- YAML objects `{symbol: SYMBOL, interval: INTERVAL}`

Supported intervals: `1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h` (enforced in schema).

## Backtest (two‑sided)

Reads OHLCV from TimescaleDB using the DSN in `qryptify_ingestor/config.yaml`.

Examples (use console scripts or the Python module)

```bash
# EMA 50/200 on 4h
qryptify-backtest --pair BTCUSDT/4h --strategy ema --lookback 100000 \
  --fast 50 --slow 200 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0

# Bollinger 50 × 3.0 on 1h
qryptify-backtest --pair BTCUSDT/1h --strategy bollinger --lookback 100000 \
  --bb-period 50 --bb-mult 3.0 --equity 10000 --risk 0.005 --atr 14 --atr-mult 2.0 --slip-bps 1

# RSI with EMA filter on 15m
qryptify-backtest --pair BTCUSDT/15m --strategy rsi --lookback 100000 \
  --rsi-period 14 --rsi-entry 30 --rsi-exit 55 --rsi-ema 200 --equity 10000 --risk 0.005 --atr 14 --atr-mult 3.0 --slip-bps 1
```

Highlights

- Strategies: `ema`, `bollinger`, `rsi` (two‑sided)
- Window: `--lookback` or `--start/--end`
- Risk: `--equity`, `--risk`, `--atr`, `--atr-mult`, `--slip-bps`, optional trailing `--atr-trail`, `--atr-trail-trigger`
- Per‑strategy params as shown in examples
- Fees: resolves taker bps per symbol from Binance API at run time (fallback 4.0 bps); override with `--fee-bps`
- Execution model: signals on close; entries/exits at next open with slippage; stops can gap; sizing via ATR; optional lot/minNotional/tick constraints

## Optimizer

Sweep strategies and parameters across pairs and export results under `reports/`.

```bash
# Single pair with Pareto CSVs and Markdown summary
qryptify-optimize --pair BTCUSDT/1h \
  --lookback 100000 --strategies ema,bollinger,rsi \
  --fast 10,20,30,50 --slow 50,100,200 \
  --risk 0.003,0.005,0.01 --atr-mult 2.0,2.5,3.0 \
  --dd-cap 3000 --lam 0.5 --top-k 10 \
  --out reports/optimizer_results.csv \
  --full-out reports/optimizer_full_grid.csv \
  --pareto-dir reports/pareto --md-out reports/optimizer_summary.md

# Or drive via YAML (pairs, strategies, grids, overrides)
qryptify-optimize --config qryptify_ingestor/config.yaml \
  --out reports/optimizer_results.csv --pareto-dir reports/pareto --md-out reports/optimizer_summary.md
```

Outputs

- Best‑per‑pair CSV (`optimizer_results.csv`)
- Optional full grid CSV (`optimizer_full_grid.csv`)
- Per‑pair Pareto frontier CSVs (maximize PnL, minimize DD)
- Markdown summary with a runnable Reproduce command per pair

Fees note: this repo does not maintain historical fee snapshots; strategy tools use API bps by default.

## Repo Map

- `qryptify_ingestor/` — Binance client, backfill/live runners, Timescale repo
- `qryptify_strategy/` — backtester, strategies, optimizer
- `sql/` — Timescale schema (`001_init.sql`) and strategy tables (`002_strategy.sql`)

## Dev & Formatting

This repo uses pre-commit with isort (google), YAPF, and Prettier.

```bash
pip install pre-commit
pre-commit install
pre-commit run -a
```

Run hooks again if they modify files.

### Local Dev Tips

- Install dev dependencies so `ruff`, `mypy`, and `pytest` are available:

```bash
python -m pip install -e ".[dev]"
```

- Lint, type-check, and test (using this env’s Python):

```bash
python -m ruff check .
python -m mypy --explicit-package-bases --module qryptify --module qryptify_ingestor --module qryptify_strategy
python -m pytest -q
```

- Optional live buffering: add to `qryptify_ingestor/config.yaml` to batch live upserts (default is 1):

```yaml
live:
  buffer_max: 10
```
