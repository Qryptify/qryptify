# Qryptify

Simple trading playground with two parts:

- Ingestor: streams Binance Futures klines into TimescaleDB.
- Strategy: backtests bar-close strategies on stored OHLCV.

## Ingestor

Start TimescaleDB and ingest data:

```bash
docker compose up -d
python main.py
./verify_ingestion.sh
```

## Strategy Backtests

The CLI reads the DB DSN from `qryptify_ingestor/config.yaml`.

Example (EMA 50/200 on 4h):

```bash
python -m qryptify_strategy.backtest --pair BTCUSDT/4h --strategy ema --lookback 2000 \
  --fast 50 --slow 200 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0
```

Short‑TF example (RSI scalping on 15m):

```bash
python -m qryptify_strategy.backtest --pair BTCUSDT/15m --strategy rsi \
  --rsi-period 8 --rsi-entry 28 --rsi-exit 58 --rsi-ema 50 \
  --lookback 3000 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0
```

Options:

- `--pair`: `SYMBOL/interval` (e.g., `ETHUSDT/4h`)
- `--strategy`: `ema`, `bollinger`, `rsi` (default `ema`)
- `--lookback` or `--start`/`--end` (ISO UTC)
- Risk: `--equity`, `--risk`, `--atr`, `--atr-mult`, `--fee-bps`, `--slip-bps`
- EMA: `--fast`, `--slow`
- Bollinger: `--bb-period`, `--bb-mult`
- RSI: `--rsi-period`, `--rsi-entry`, `--rsi-exit`, `--rsi-ema`
- Exchange constraints: `--qty-step`, `--min-qty`, `--min-notional`, `--price-tick`

Execution model:

- Signals on bar close; fills at next bar open with slippage.
- Stops may trigger intrabar; gap‑through exits at open with slippage.
- Sizing uses ATR risk; orders respect lot step, min notional, and tick size.

Schema (optional):

- `sql/002_strategy.sql` creates `orders` and `trades` for future paper/live tracking.
