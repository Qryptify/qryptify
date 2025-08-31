# Qryptify Data Ingestor

## Overview

The **Qryptify Data Ingestor** is a service that:

- Backfills historical candlestick (kline) data from Binance **Futures** API into TimescaleDB.
- Streams **real-time** closed candlesticks via Binance WebSocket API.
- Ensures **no duplicates** and **resumes from last saved candle** after downtime.

It is the foundation for backtesting, live trading, and analytics in the Qryptify trading system.

## Features

- **Historical Backfill** from a configurable start date.
- **Live WebSocket Streaming** with sub-second latency after candle close.
- **TimescaleDB Hypertable Storage** for efficient time-series queries.
- **Resume on Restart** using a per-symbol `sync_state`.
- **Idempotent Inserts** via `(symbol, interval, ts)` primary key.

## Architecture

```text
+---------------------+        REST (backfill)        +---------------------+
|  Ingestion Service  |------------------------------>|  Binance Futures    |
|  (main.py)          |                                |  API (REST/WSS)     |
|                     |<------- WebSocket (live) ---->|  /fapi/v1/klines    |
+----------+----------+                                +----------+----------+
           |  upsert (no duplicates)                              |
           v                                                      |
+---------------------+      hypertables/unique keys              |
|   TimescaleDB       |<------------------------------------------+
|  candlesticks       |
|  sync_state         |
+---------------------+
```

## Requirements

- **Python** 3.10+
- **Docker** (for TimescaleDB)
- Binance Futures API access (public endpoints only for this MVP)

## Setup

### 1. Start TimescaleDB

```bash
docker compose up -d
```

This runs TimescaleDB on port **5432** with:

- DB: `qryptify`
- User: `postgres`
- Password: `postgres`

Schema & hypertables are auto-created via `sql/001_init.sql`.

### 2. Install Dependencies

```bash
pip install httpx websockets pyyaml "psycopg[binary]" tenacity pytz
```

### 3. Configure

Edit `qryptify_ingestor/config.yaml`.

### 4. Run

```bash
python main.py
```

- Step 1: Backfills from `start_date` → current time.
- Step 2: Switches to WebSocket live mode and runs until stopped.

Stop with **Ctrl + C** (safe; progress is saved in DB).

## Verifying Data

Use the provided script:

```bash
./verify_ingestion.sh
```

This checks:

1. TimescaleDB extension installed.
2. Hypertables exist.
3. Coverage per symbol/interval.
4. Resume pointer (`sync_state`).
5. Duplicate key sanity.
6. Live data lag from now.

Example:

```text
============================================================
4) Candle coverage per (symbol, interval)
============================================================
BTCUSDT  1m   2023-01-01 00:00:00+00   2025-08-10 09:50:00+00   1234567
ETHUSDT  1m   2023-01-01 00:00:00+00   2025-08-10 09:50:00+00   1234567
BNBUSDT  1m   2023-01-01 00:00:00+00   2025-08-10 09:50:00+00   1234567
```
