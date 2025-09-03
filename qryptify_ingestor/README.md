# Qryptify Ingestor

Binance Futures kline ingestor. Backfills historical data, streams closed candles live, and stores everything in TimescaleDB with safe, idempotent writes.

## Features

- Backfills historical klines for configured pairs (symbol/interval)
- Streams closed candles via WebSocket and appends to DB
- Idempotent upserts into a TimescaleDB hypertable (no duplicates)
- Resume pointers per pair to continue after restarts

## Requirements

- Python 3.10+
- Docker (TimescaleDB via `docker-compose.yml`)

Start TimescaleDB and initialize schema:

```bash
docker compose up -d
```

The `sql/001_init.sql` initializes the hypertable (`candlesticks`) and resume table (`sync_state`), with compression policies.

## Install

Install the package in editable mode (includes dependencies and console scripts):

```bash
python -m pip install -e .
```

## Configure

Edit `qryptify_ingestor/config.yaml`:

```yaml
pairs:
  - BTCUSDT/4h
  - ETHUSDT/1h
  - { symbol: BNBUSDT, interval: 15m }
rest:
  endpoint: https://fapi.binance.com
  klines_limit: 1500
ws:
  endpoint: wss://fstream.binance.com/stream
db:
  dsn: postgresql://postgres:postgres@localhost:5432/qryptify
backfill:
  start_date: "2022-01-01T00:00:00Z"
```

Notes

- Pair formats: `SYMBOL/interval`, `SYMBOL-interval`, or `{symbol, interval}`
- Supported intervals: `1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h`
- `db.dsn` is also used by the strategy/optimizer to read OHLCV for backtests

## Run

```bash
qryptify-ingest   # or: python main.py
```

Flow

- Backfills from the later of `backfill.start_date` or the last saved close per pair
- Switches to live streaming and appends new closed candles
- Ctrl+C to stop; resume pointers are saved in `sync_state` (a benign WebSocket close trace may appear)
- Optional: live batching with `live.buffer_max` (default 1). Buffered rows are flushed on shutdown.

## Verify

```bash
./verify_ingestion.sh
```

Shows Timescale extension status, hypertables, table coverage per pair, resume pointers, and 1m lag.

Tip: set `PG*` env vars (e.g., `PGPASSWORD`) to avoid prompts.

## Seed sample data

You can seed synthetic OHLCV for quick tests:

```bash
qryptify-seed --pair BTCUSDT/1h --rows 500
```

## Reset DB (clean slate)

To wipe all data and reinitialize schema/hypertables:

```bash
./reset_db.sh      # confirm prompt
./reset_db.sh -f   # skip confirmation
```

## Schema (brief)

- `candlesticks` hypertable on `ts`, 1‑day chunks
  - PK `(symbol, interval, ts)` ensures idempotent upsert
  - Compression enabled (order by `ts DESC`, segment by `symbol, interval`), policy after 7 days
- `sync_state(symbol, interval, last_closed_ts)` stores last closed candle per pair

Conventions: `symbol` uppercased; OHLCV stored as DOUBLE PRECISION for speed.

## Internals

- REST (`backfill_runner.py`): paginates `/fapi/v1/klines` from the resume pointer until near‑now
- WebSocket (`live_runner.py`): subscribes per‑pair streams; writes only closed klines (`x = true`)
- Timescale access: `qryptify/data/timescale.py` (`TimescaleRepo`, `AsyncTimescaleRepo`)
- `coordinator.py`: orchestrates backfill then live; retries on transient errors (tenacity)

## Fees

This repo does not include a fee snapshot table or script. Strategy tools fetch current taker bps from Binance’s API per symbol at run time (fallback 4.0 bps). If you want historical, time‑varying fees, manage that externally.

## Using with qryptify_strategy

- The backtester/optimizer reads the same DSN (`qryptify_ingestor/config.yaml`) to load OHLCV. Fees are resolved from API at run time.
- You can pass the same YAML into the optimizer’s `--config` to iterate pairs/strategies and export results.
