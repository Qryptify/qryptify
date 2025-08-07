#!/bin/bash
# Reset last sync file and run the CLI for a clean, observable run
set -e
LAST_SYNC_FILE=".data/last_crawl_binance_candlesticks_realtime_BTCUSDT_60.txt"
if [ -f "$LAST_SYNC_FILE" ]; then
  rm "$LAST_SYNC_FILE"
else
  mkdir -p $(dirname "$LAST_SYNC_FILE")
fi
echo 0 > "$LAST_SYNC_FILE"
PYTHONPATH=. python3 -m qryptify.cli.binance_candlestick_crawler --output_db postgresql://postgres:password@localhost/qryptify --coin BTC --time-interval 60
