-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Optional: symbols registry (handy for joins later)
CREATE TABLE IF NOT EXISTS symbols (
  symbol TEXT PRIMARY KEY
);

INSERT INTO symbols(symbol) VALUES
('BTCUSDT'), ('ETHUSDT'), ('BNBUSDT')
ON CONFLICT DO NOTHING;

-- Candlesticks hypertable
CREATE TABLE IF NOT EXISTS candlesticks (
  ts TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL,
  interval TEXT NOT NULL,
  open NUMERIC NOT NULL,
  high NUMERIC NOT NULL,
  low  NUMERIC NOT NULL,
  close NUMERIC NOT NULL,
  volume NUMERIC NOT NULL,
  close_time TIMESTAMPTZ NOT NULL,
  quote_asset_volume NUMERIC NOT NULL,
  number_of_trades INT NOT NULL,
  taker_buy_base NUMERIC NOT NULL,
  taker_buy_quote NUMERIC NOT NULL,
  PRIMARY KEY (symbol, interval, ts)
);

SELECT create_hypertable('candlesticks', 'ts', if_not_exists => TRUE);

-- Sync state for resume
CREATE TABLE IF NOT EXISTS sync_state (
  symbol TEXT NOT NULL,
  interval TEXT NOT NULL,
  last_closed_ts TIMESTAMPTZ,
  PRIMARY KEY (symbol, interval)
);

-- Helpful index for time filters per symbol/interval
CREATE INDEX IF NOT EXISTS idx_candles_sym_int_ts
ON candlesticks(symbol, interval, ts DESC);
