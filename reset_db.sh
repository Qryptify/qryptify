#!/usr/bin/env bash
set -euo pipefail

# Reset the TimescaleDB used by Qryptify by removing the Docker volume and
# bringing the service back up so that /docker-entrypoint-initdb.d scripts
# (e.g., sql/001_init.sql) run again.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

usage() {
  cat <<'USAGE'
Reset Qryptify TimescaleDB by deleting the Docker volume and reinitializing.

Usage: ./reset_db.sh [options]

Options:
  -f, --force      Skip confirmation prompt
      --no-up      Do not start the DB after removal (just remove volume)
      --no-verify  Skip post-up verification
  -h, --help       Show this help

Notes:
  - This is DESTRUCTIVE. All database data will be lost.
  - Recreating the container will auto-run sql/001_init.sql.
USAGE
}

# Defaults
FORCE=0
RUN_UP=1
VERIFY=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    -f|--force) FORCE=1; shift ;;
    --no-up) RUN_UP=0; shift ;;
    --no-verify) VERIFY=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

# Pick docker compose variant
if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  echo "Error: docker compose not found. Install Docker Desktop or docker-compose." >&2
  exit 1
fi

if [[ $FORCE -ne 1 ]]; then
  echo "WARNING: This will DELETE all database data (Docker volume)."
  read -r -p "Type 'RESET' to proceed: " ANSWER
  if [[ "$ANSWER" != "RESET" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

echo "[1/3] Bringing down stack and removing volumes..."
"${COMPOSE[@]}" down -v

if [[ $RUN_UP -eq 0 ]]; then
  echo "Done. Stack is down and volume removed."
  exit 0
fi

echo "[2/3] Starting db..."
"${COMPOSE[@]}" up -d db

echo "[3/3] Waiting for container health (qryptify_db)..."
ATTEMPTS=0
MAX_ATTEMPTS=60
SLEEP_SECS=5

until STATUS=$(docker inspect -f '{{.State.Health.Status}}' qryptify_db 2>/dev/null || echo 'missing'); do
  sleep 1
done

while [[ "$STATUS" != "healthy" && $ATTEMPTS -lt $MAX_ATTEMPTS ]]; do
  ATTEMPTS=$((ATTEMPTS+1))
  echo "  - status: $STATUS (attempt $ATTEMPTS/$MAX_ATTEMPTS)"
  sleep "$SLEEP_SECS"
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' qryptify_db 2>/dev/null || echo 'missing')
done

if [[ "$STATUS" != "healthy" ]]; then
  echo "Container did not become healthy in time. Showing recent logs:" >&2
  docker logs --tail 200 qryptify_db || true
  exit 1
fi

echo "DB is healthy. Initialization scripts should have run."

if [[ $VERIFY -eq 1 ]]; then
  if [[ -x ./verify_ingestion.sh ]]; then
    echo "Running verify_ingestion.sh..."
    ./verify_ingestion.sh || true
  else
    echo "Tip: run ./verify_ingestion.sh to validate schema/hypertables."
  fi
fi

echo "Reset complete."
