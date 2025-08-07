# qryptify

**Qryptify** is a cryptocurrency data crawler focused on Binance USDT-margined futures. It provides tools to collect real-time trade prices and candlestick data, storing them in TimescaleDB for further analysis or downstream processing.

## Features

- Real-time trade price crawling for supported Binance futures pairs
- Real-time candlestick (OHLCV) crawling with customizable intervals
- Easy integration with TimescaleDB
- Extensible CLI for additional data sources

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. Realtime Trade Price Crawler

Fetches real-time trade prices for a given coin (e.g., BTCUSDT) and stores them in TimescaleDB.

```bash
python3 run.py binance_price_realtime_crawler -c BTC -o "localhost"
```

### 2. Realtime Candlestick Crawler

Fetches real-time candlestick (OHLCV) data for a given coin and interval, storing results in TimescaleDB.

```bash
python3 run.py binance_candlestick_crawler -c BTC -o "localhost" -t 3600
```

## CLI Parameters

- `-c`, `--coin`: Coin symbol (e.g., BTC; will be treated as BTCUSDT)
- `-o`, `--output_db`: TimescaleDB connection string or host (default: localhost)
- `-t`, `--time-interval`: Candlestick interval in seconds (supported: 60, 180, 300, 900, 1800, 3600, 7200, 14400, 21600, 28800, 43200, 86400, 259200, 604800, 2592000)

## Connect to the Database

```bash
psql -h localhost -U postgres -d qryptify
```
