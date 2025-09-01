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

Start TimescaleDB and create the schema:

```bash
docker compose up -d
```

The `sql/001_init.sql` initializes the hypertable (`candlesticks`) and resume table (`sync_state`), with compression policies.
`sql/003_fees.sql` defines `exchange_fees` used by the strategy/optimizer; the
snapshot script can also create it if missing.

## Install

```bash
pip install httpx websockets pyyaml "psycopg[binary]" tenacity pytz loguru
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
python main.py
```

Flow

- Backfills from the later of `backfill.start_date` or the last saved close per pair
- Switches to live streaming and appends new closed candles
- Ctrl+C to stop; resume pointers are saved in `sync_state`. A benign
  `KeyboardInterrupt` trace from the WebSocket close may appear.

## Verify

```bash
./verify_ingestion.sh
```

Shows Timescale extension status, hypertables, table coverage per pair, resume pointers, and 1m lag.

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
- `timescale_repo.py`: thin, explicit Timescale access (connect/close, upsert, fetch, resume)
- `coordinator.py`: orchestrates backfill then live; has retry on transient errors

## Fee snapshots

Strategy backtests and optimizer can apply time‑varying exchange fees from the DB.

Insert a snapshot (maker/taker bps per symbol) for all pairs configured in your YAML:

```bash
python -m qryptify_ingestor.fees_snapshot --config qryptify_ingestor/config.yaml
```

This writes to `exchange_fees(symbol, ts, maker_bps, taker_bps, source, note)`.
Snapshots are sparse and only created when you run the script; schedule it periodically if your account tier changes.

## Using with qryptify_strategy

- The backtester/optimizer reads the same DSN (`qryptify_ingestor/config.yaml`) to load OHLCV and fee snapshots
- You can pass the same YAML into the optimizer’s `--config` to iterate pairs/strategies and export results
