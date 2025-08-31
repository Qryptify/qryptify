# Qryptify Ingestor

Simple Binance Futures kline ingestor that backfills history, streams live candle closes, and stores data in TimescaleDB with safe, idempotent writes.

## What it does

- Backfills historical klines per configured pairs
- Streams closed candles over WebSocket
- Upserts into a TimescaleDB hypertable (no duplicates)
- Persists resume pointers per pair to continue after restarts

## Prereqs

- Python 3.10+
- Docker (TimescaleDB via `docker-compose.yml`)

Start the DB (schema auto-creates from `sql/001_init.sql`):

```bash
docker compose up -d
```

## Install

```bash
pip install httpx websockets pyyaml "psycopg[binary]" tenacity pytz loguru
```

## Configure

Edit `qryptify_ingestor/config.yaml`.

Notes:

- Pair formats supported: `SYMBOL/interval`, `SYMBOL-interval`, or `{symbol, interval}`
- Allowed intervals: `1m, 3m, 5m, 15m, 1h, 4h`

## Run

```bash
python main.py
```

Flow:

- Backfill from `backfill.start_date` or last saved close
- Switch to live mode and append closed candles

Stop with Ctrl+C. Progress is saved in `sync_state`.

## Verify

```bash
./verify_ingestion.sh
```

Shows the Timescale extension, hypertables, coverage, resume pointers, and lag.

## Reset DB (clean slate)

To wipe all data and reinitialize schema/hypertables:

```bash
./reset_db.sh      # prompts confirm, recreates DB, waits healthy
./reset_db.sh -f   # skip confirmation
```

## Schema (brief)

- Table: `candlesticks` (hypertable on `ts`, 1-day chunks)
- PK: `(symbol, interval, ts)` to ensure idempotency
- Compression: enabled with `compress_orderby = ts DESC`, `compress_segmentby = symbol, interval`; policy after 7 days
- Resume: `sync_state(symbol, interval, last_closed_ts)`

Conventions: `symbol` uppercased; numeric columns use double precision for performance.
