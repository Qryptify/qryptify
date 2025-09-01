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
python -m qryptify_strategy.backtest --pair BTCUSDT/4h --strategy ema --lookback 2000 \
  --fast 50 --slow 200 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0

# Two-sided EMA (long/short) on 1h
python -m qryptify_strategy.backtest --pair BTCUSDT/1h --strategy ema_ls --lookback 32132 --fast 50 --slow 200 --equity 10000 --risk 0.01 --atr 14 --atr-mult 2.0 --fee-bps 4 --slip-bps 1

# RSI scalping on 15m
python -m qryptify_strategy.backtest --pair BTCUSDT/15m --strategy rsi \
  --rsi-period 8 --rsi-entry 28 --rsi-exit 58 --rsi-ema 50 --lookback 3000
```

Options:

- `--pair`: `SYMBOL/interval`
- `--strategy`: `ema`, `ema_ls` (long/short), `bollinger`, `rsi`
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

- EMA crossover (long/flat)
- EMA crossover long/short (two-sided trend)
- Bollinger breakout (long/flat)
- RSI mean-reversion with optional EMA filter (5m/15m friendly)

## Code Map

- `qryptify_strategy/backtest.py` — CLI
- `qryptify_strategy/backtester.py` — engine (ATR sizing, stops, fees/slippage)
- `qryptify_strategy/strategies/` — strategy implementations
- `qryptify_strategy/indicators.py` — EMA, WilderRSI, WilderATR, RollingMeanStd, true_range
