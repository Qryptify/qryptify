-- Strategy-related minimal schema: orders and trades (for paper/backtest/live)

CREATE TABLE IF NOT EXISTS orders (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  strategy_id TEXT NOT NULL,
  symbol TEXT NOT NULL CHECK (symbol = upper(symbol)),
  side TEXT NOT NULL CHECK (side IN ('BUY','SELL')),
  qty DOUBLE PRECISION NOT NULL CHECK (qty > 0),
  price DOUBLE PRECISION NOT NULL CHECK (price > 0),
  status TEXT NOT NULL CHECK (status IN ('NEW','FILLED','CANCELLED','REJECTED','PAPER_FILLED')) DEFAULT 'NEW',
  source TEXT NOT NULL DEFAULT 'paper',
  note TEXT
);

CREATE INDEX IF NOT EXISTS idx_orders_strategy_ts ON orders(strategy_id, ts);
CREATE INDEX IF NOT EXISTS idx_orders_symbol_ts ON orders(symbol, ts);

CREATE TABLE IF NOT EXISTS trades (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  symbol TEXT NOT NULL CHECK (symbol = upper(symbol)),
  side TEXT NOT NULL CHECK (side IN ('BUY','SELL')),
  qty DOUBLE PRECISION NOT NULL CHECK (qty > 0),
  price DOUBLE PRECISION NOT NULL CHECK (price > 0),
  fee DOUBLE PRECISION NOT NULL DEFAULT 0,
  pnl DOUBLE PRECISION NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_trades_order ON trades(order_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_ts ON trades(symbol, ts);
