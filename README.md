# data-crawler
Futures Data Crawler

## Installation

```bash
pip install -r requirements.txt
```

## How to Run

### 1. Realtime Trade Price Crawler

```bash
python3 run.py binance_price_realtime_crawler -c BTC -o "mongodb://localhost:27017/"
```

### 2. Realtime Candlestick Crawler

```bash
python3 run.py binance_candlestick_crawler -c BTC -o "mongodb://localhost:27017/" -t 3600
```

## Parameters

- `-c`: Coin symbol (e.g., BTC; will be treated as BTCUSDT)
- `-o`: MongoDB connection string
- `-t`: Candlestick interval in seconds (e.g. 60 = 1m, 3600 = 1h, 86400 = 1d)