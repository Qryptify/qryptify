import os

from click.testing import CliRunner
import psycopg2
import pytest

DB_URL = 'postgresql://postgres:password@localhost/qryptify'
PRICES_TABLE = 'prices'
CANDLES_TABLE = 'candlesticks'


@pytest.fixture
def db_conn():
    conn = psycopg2.connect(DB_URL)
    yield conn
    conn.close()


def count_rows(conn, table):
    with conn.cursor() as cur:
        cur.execute(f'SELECT COUNT(*) FROM {table}')
        return cur.fetchone()[0]


def test_cli_updates_db(db_conn):
    from qryptify.cli import cli
    runner = CliRunner()
    # Reset last sync file to 0 to force fetching old candles
    last_sync_file = '.data/last_crawl_binance_candlesticks_realtime_BTCUSDT_60.txt'
    if os.path.exists(last_sync_file):
        os.remove(last_sync_file)
    else:
        os.makedirs(os.path.dirname(last_sync_file), exist_ok=True)
    with open(last_sync_file, 'w') as f:
        f.write('0\n')

    # Count rows before
    prices_before = count_rows(db_conn, PRICES_TABLE)
    candles_before = count_rows(db_conn, CANDLES_TABLE)
    # Run CLI with test params (adjust as needed for your CLI)
    result = runner.invoke(cli, [
        'binance_candlestick_crawler', '--output_db', DB_URL, '--coin', 'BTC',
        '--time-interval', '60', '--fetch-limit', '5'
    ])
    # Count rows after
    prices_after = count_rows(db_conn, PRICES_TABLE)
    candles_after = count_rows(db_conn, CANDLES_TABLE)
    assert result.exit_code == 0 or result.exit_code == 1
    assert prices_after > prices_before or candles_after > candles_before
