#!/usr/bin/env bash
set -euo pipefail

# Verify TimescaleDB + ingestion status with readable, informative output.
#
# Options via env vars:
#   PGHOST, PGPORT, PGUSER, PGDATABASE, PGPASSWORD  - connection settings
#   FILTER_SYMBOL  - limit to a specific symbol (e.g., BTCUSDT)
#   FILTER_INTERVAL - limit to a specific interval (e.g., 1h)
#   SHOW_SAMPLE=1  - also show last 3 bars per (symbol, interval)

# --- Config (override via env) ---
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-qryptify}"
PGPASSWORD="${PGPASSWORD:-postgres}"   # export PGPASSWORD=... to avoid prompts

PSQL="psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -v ON_ERROR_STOP=1 -X -q -A -F $'\t'"

FILTER_SYMBOL="${FILTER_SYMBOL:-}"
FILTER_INTERVAL="${FILTER_INTERVAL:-}"
SHOW_SAMPLE="${SHOW_SAMPLE:-0}"

# --- Display helpers ---
bold()   { tput bold 2>/dev/null || true; }
normal() { tput sgr0 2>/dev/null || true; }
green()  { tput setaf 2 2>/dev/null || true; }
cyan()   { tput setaf 6 2>/dev/null || true; }
yellow() { tput setaf 3 2>/dev/null || true; }
red()    { tput setaf 1 2>/dev/null || true; }

bar() {
  printf "\n"; bold; printf "============================================================\n"; normal
  bold; cyan; printf "%s\n" "$1"; normal
  bold; printf "============================================================\n"; normal
}

pretty() {
  # Align TSV into columns for readability
  column -t -s $'\t'
}

# Build filters
SYM_F=$(printf %s "$FILTER_SYMBOL" | tr '[:lower:]' '[:upper:]')
IVL_F=$(printf %s "$FILTER_INTERVAL" | tr -d '[:space:]')
WHERE_SYM="1=1"; [[ -n "$SYM_F" ]] && WHERE_SYM="symbol='${SYM_F}'"
WHERE_IVL="1=1"; [[ -n "$IVL_F" ]] && WHERE_IVL="interval='${IVL_F}'"

bar "0) Connection"
echo "$(bold)Host:$(normal) $PGHOST  $(bold)DB:$(normal) $PGDATABASE  $(bold)User:$(normal) $PGUSER"
if [[ -n "$SYM_F" || -n "$IVL_F" ]]; then
  echo "$(bold)Filter:$(normal) symbol=${SYM_F:-ALL} interval=${IVL_F:-ALL}"
fi

bar "1) Extensions & Server"
$PSQL -c "SELECT extname, extversion FROM pg_extension ORDER BY 1;" | pretty
$PSQL -c "SELECT version() AS server_version, current_database() AS db, current_schema AS schema;" | pretty

bar "2) Database & Table Sizes"
$PSQL -c "SELECT pg_size_pretty(pg_database_size(current_database())) AS db_size;" | pretty
$PSQL -c "
SELECT relname AS table,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
       pg_size_pretty(pg_relation_size(relid))       AS heap,
       pg_size_pretty(pg_indexes_size(relid))        AS indexes
FROM pg_catalog.pg_statio_user_tables
WHERE relname IN ('candlesticks','sync_state')
ORDER BY 1;" | pretty

bar "3) Timescale Hypertables"
$PSQL -c "
SELECT h.hypertable_schema, h.hypertable_name, h.num_chunks, h.compression_enabled,
       COALESCE(SUM(CASE WHEN c.is_compressed THEN 1 ELSE 0 END),0) AS compressed_chunks
FROM timescaledb_information.hypertables h
LEFT JOIN timescaledb_information.chunks c
  ON c.hypertable_schema=h.hypertable_schema AND c.hypertable_name=h.hypertable_name
GROUP BY 1,2,3,4
ORDER BY 1,2;" | pretty

bar "4) Tables Present"
$PSQL -c "SELECT schemaname, tablename, tableowner FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1,2;" | pretty

bar "5) Candle Coverage per (symbol, interval) + Completeness"
$PSQL -c "
WITH agg AS (
  SELECT symbol, interval, MIN(ts) AS first_open, MAX(ts) AS last_open, COUNT(*) AS rows
  FROM candlesticks
  WHERE $WHERE_SYM AND $WHERE_IVL
  GROUP BY symbol, interval
), spb AS (
  SELECT * FROM (VALUES
    ('1m',60), ('3m',180), ('5m',300), ('15m',900), ('30m',1800), ('1h',3600), ('2h',7200), ('4h',14400)
  ) AS v(interval, spb)
)
SELECT a.symbol, a.interval, a.first_open, a.last_open, a.rows,
       ROUND(((EXTRACT(EPOCH FROM (a.last_open - a.first_open)))/s.spb)+1) AS expected,
       ROUND(100.0 * a.rows / NULLIF(ROUND(((EXTRACT(EPOCH FROM (a.last_open - a.first_open)))/s.spb)+1),0), 2) AS pct
FROM agg a JOIN spb s USING (interval)
ORDER BY a.symbol, a.interval;" | pretty

bar "6) Resume Pointers vs Stored Candles"
$PSQL -c "
SELECT s.symbol, s.interval, s.last_closed_ts,
       MAX(c.ts) AS last_open,
       (MAX(c.ts) - s.last_closed_ts) AS gap
FROM sync_state s
LEFT JOIN candlesticks c ON c.symbol=s.symbol AND c.interval=s.interval
WHERE $WHERE_SYM AND $WHERE_IVL
GROUP BY s.symbol, s.interval, s.last_closed_ts
ORDER BY 1,2;" | pretty

bar "7) Duplicate Check (PK uniqueness sanity)"
$PSQL -c "
WITH t AS (
  SELECT symbol, interval, ts FROM candlesticks WHERE $WHERE_SYM AND $WHERE_IVL
)
SELECT
  (SELECT COUNT(*) FROM t) AS total_rows,
  (SELECT COUNT(*) FROM (SELECT DISTINCT symbol, interval, ts FROM t) d) AS distinct_rows;" | pretty

bar "8) Live Lag (per symbol, interval)"
$PSQL -c "
WITH latest AS (
  SELECT symbol, interval, MAX(ts) AS last_open
  FROM candlesticks
  WHERE $WHERE_SYM AND $WHERE_IVL
  GROUP BY symbol, interval
)
SELECT symbol, interval, last_open,
       now() AT TIME ZONE 'utc' AS now_utc,
       (now() AT TIME ZONE 'utc') - last_open AS lag
FROM latest
ORDER BY 1,2;" | pretty

if [[ "${SHOW_SAMPLE}" == "1" ]]; then
  bar "9) Sample: Last 3 Bars per (symbol, interval)"
  $PSQL -c "
  SELECT symbol, interval, ts, open, high, low, close, volume
  FROM (
    SELECT symbol, interval, ts, open, high, low, close, volume,
           ROW_NUMBER() OVER (PARTITION BY symbol, interval ORDER BY ts DESC) AS rn
    FROM candlesticks
    WHERE $WHERE_SYM AND $WHERE_IVL
  ) t
  WHERE rn <= 3
  ORDER BY symbol, interval, ts DESC;" | pretty
fi

bar "Done"
