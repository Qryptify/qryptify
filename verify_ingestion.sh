#!/usr/bin/env bash
set -euo pipefail

# --- Config (override via env) ---
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-qryptify}"
PGPASSWORD="${PGPASSWORD:-postgres}"   # export PGPASSWORD=... to avoid prompts

PSQL="psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -v ON_ERROR_STOP=1 -X -q -A -F $'\t'"

bar() { printf "\n============================================================\n%s\n============================================================\n" "$1"; }

bar "1) Extensions installed"
$PSQL -c "SELECT extname FROM pg_extension ORDER BY 1;"

bar "2) Timescale hypertables"
$PSQL -c "SELECT hypertable_schema, hypertable_name, num_chunks, compression_enabled
          FROM timescaledb_information.hypertables
          ORDER BY 1,2;"

bar "3) Tables present"
$PSQL -c "\dt"

bar "4) Candle coverage per (symbol, interval)"
$PSQL -c "
SELECT symbol, interval,
       MIN(ts)  AS first_open,
       MAX(ts)  AS last_open,
       COUNT(*) AS rows
FROM candlesticks
GROUP BY 1,2
ORDER BY 1,2;"

bar "5) Resume pointers (sync_state)"
$PSQL -c "SELECT symbol, interval, last_closed_ts
          FROM sync_state
          ORDER BY 1,2;"

bar "6) Duplicate check (PK uniqueness sanity)"
$PSQL -c "
WITH t AS (SELECT symbol, interval, ts FROM candlesticks)
SELECT
  (SELECT COUNT(*) FROM t)                                      AS total_rows,
  (SELECT COUNT(*) FROM (SELECT DISTINCT symbol,interval,ts FROM t) d) AS distinct_rows;"

bar "7) Live lag (how far from now)"
$PSQL -c "
WITH latest AS (
  SELECT symbol, MAX(ts) AS last_open
  FROM candlesticks
  WHERE interval='1m'
  GROUP BY symbol
)
SELECT symbol,
       last_open,
       now() AT TIME ZONE 'utc' AS now_utc,
       (now() AT TIME ZONE 'utc') - last_open AS lag
FROM latest
ORDER BY 1;"

bar "Done "
