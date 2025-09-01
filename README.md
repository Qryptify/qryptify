# Qryptify

Two-part trading playground:

- Ingestor: streams Binance Futures klines into TimescaleDB.
- Strategy: backtests two‑sided strategies (long/short) on stored OHLCV and optimizes parameters.

This README gives a project overview. See component READMEs for details:

- `qryptify_ingestor/README.md`
- `qryptify_strategy/README.md`

## Quick Start

Install Python deps and start TimescaleDB:

```bash
docker compose up -d
pip install "psycopg[binary]" pyyaml loguru httpx websockets tenacity pytz
```

Edit pairs and DSN in `qryptify_ingestor/config.yaml`, then ingest:

```bash
python main.py
./verify_ingestion.sh
```

Pair formats supported in config:

- `SYMBOL/interval` (e.g., `BTCUSDT/1h`)
- `SYMBOL-interval` (e.g., `ETHUSDT-4h`)
- YAML objects `{symbol: SYMBOL, interval: INTERVAL}`

## Backtest (two‑sided)

Examples (reads DSN from `qryptify_ingestor/config.yaml`):

```bash
# EMA 50/200 on 4h
python -m qryptify_strategy.backtest --pair BTCUSDT/4h --strategy ema --lookback 100000 \
  --fast 50 --slow 200 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0

# Bollinger 50 × 3.0 on 1h
python -m qryptify_strategy.backtest --pair BTCUSDT/1h --strategy bollinger --lookback 100000 \
  --bb-period 50 --bb-mult 3.0 --equity 10000 --risk 0.005 --atr 14 --atr-mult 2.0 --slip-bps 1

# RSI with EMA filter on 15m
python -m qryptify_strategy.backtest --pair BTCUSDT/15m --strategy rsi --lookback 100000 \
  --rsi-period 14 --rsi-entry 30 --rsi-exit 55 --rsi-ema 200 --equity 10000 --risk 0.005 --atr 14 --atr-mult 3.0 --slip-bps 1
```

Key flags: `--pair`, `--strategy (ema|bollinger|rsi)`, `--lookback | --start/--end`, risk (`--equity --risk --atr --atr-mult --slip-bps`) and per‑strategy params.
Fees default to the current Binance API taker bps per symbol at run time (fallback 4.0 bps or override via `--fee-bps`).

Execution: signals on close; fills at next open (slippage). Stops can gap. ATR sizing; orders respect step/minNotional/tick.

## Optimizer

Sweep strategies/params across pairs and export:

```bash
# Single pair with Pareto CSVs and Markdown summary
python -m qryptify_strategy.optimize --pair BTCUSDT/1h \
  --lookback 100000 --strategies ema,bollinger,rsi \
  --fast 10,20,30,50 --slow 50,100,200 \
  --risk 0.003,0.005,0.01 --atr-mult 2.0,2.5,3.0 \
  --dd-cap 3000 --lam 0.5 --top-k 10 \
  --out reports/optimizer_results.csv \
  --full-out reports/optimizer_full_grid.csv \
  --pareto-dir reports/pareto --md-out reports/optimizer_summary.md

# Or drive via YAML (pairs, strategies, grids, overrides)
python -m qryptify_strategy.optimize --config qryptify_ingestor/config.yaml \
  --out reports/optimizer_results.csv --pareto-dir reports/pareto --md-out reports/optimizer_summary.md
```

Outputs under `reports/`:

- Best‑per‑pair CSV (`optimizer_results.csv`)
- Full grid CSV (`optimizer_full_grid.csv`)
- Pareto CSVs per pair (maximize PnL, minimize DD)
- Markdown summary with a Reproduce command per pair

Fee snapshots (optional if you want time‑varying fees):

This repo no longer includes fee snapshot tooling or schema; strategy tools use API bps by default.

## Repo Map

- `qryptify_ingestor/` — Binance client, backfill/live runners, Timescale repo
- `qryptify_strategy/` — backtester, strategies, optimizer
- `sql/` — Timescale schema (`001_init.sql`) and strategy tables (`002_strategy.sql`)

## Notes

- Keep `qryptify_ingestor/config.yaml` updated; both ingestor and strategy use its DSN.
- Use `./verify_ingestion.sh` to validate DB health and candle coverage.

## Dev & Formatting

This repo uses pre-commit with isort (google profile), YAPF, and Prettier.

```bash
pip install pre-commit
pre-commit install
# Format/lint everything
pre-commit run -a
```

If a hook modifies a file, run it again until it passes.
