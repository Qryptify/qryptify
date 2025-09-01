-- Exchange fee snapshots (evolving over time; used for backtests)

CREATE TABLE IF NOT EXISTS exchange_fees (
  ts TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL CHECK (symbol = upper(symbol)),
  maker_bps DOUBLE PRECISION NOT NULL,
  taker_bps DOUBLE PRECISION NOT NULL,
  source TEXT NOT NULL DEFAULT 'binance_fapi',
  note TEXT,
  PRIMARY KEY (symbol, ts)
);

-- Hypertable optional; sparse updates, but keep consistent
SELECT create_hypertable('exchange_fees', 'ts', if_not_exists => TRUE, chunk_time_interval => INTERVAL '30 days');

CREATE INDEX IF NOT EXISTS idx_exchange_fees_symbol_ts ON exchange_fees(symbol, ts DESC);
