CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Candlesticks hypertable
-- Notes:
-- - Use DOUBLE PRECISION for numeric performance (Binance numbers are decimal strings)
-- - Keep symbol uppercase for consistency
-- - Restrict interval to supported set (adjust as needed)
CREATE TABLE IF NOT EXISTS candlesticks (
  ts TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL CHECK (symbol = upper(symbol)),
  interval TEXT NOT NULL CHECK (interval IN ('1m','3m','5m','15m','1h')),
  open DOUBLE PRECISION NOT NULL,
  high DOUBLE PRECISION NOT NULL,
  low  DOUBLE PRECISION NOT NULL,
  close DOUBLE PRECISION NOT NULL,
  volume DOUBLE PRECISION NOT NULL,
  close_time TIMESTAMPTZ NOT NULL,
  quote_asset_volume DOUBLE PRECISION NOT NULL,
  number_of_trades INT NOT NULL,
  taker_buy_base DOUBLE PRECISION NOT NULL,
  taker_buy_quote DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (symbol, interval, ts)
);

-- Create hypertable with 1 day chunking
SELECT create_hypertable('candlesticks', 'ts', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');

-- Enable compression by (symbol, interval) for older data (7 days)
ALTER TABLE candlesticks SET (timescaledb.compress);
ALTER TABLE candlesticks SET (timescaledb.compress_segmentby = 'symbol, interval');
SELECT add_compression_policy('candlesticks', INTERVAL '7 days');

-- Sync state for resume
CREATE TABLE IF NOT EXISTS sync_state (
  symbol TEXT NOT NULL CHECK (symbol = upper(symbol)),
  interval TEXT NOT NULL CHECK (interval IN ('1m','3m','5m','15m','1h')),
  last_closed_ts TIMESTAMPTZ,
  PRIMARY KEY (symbol, interval)
);
