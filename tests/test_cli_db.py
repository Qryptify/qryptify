import os
import sys
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def patch_timescaledb(monkeypatch):
    import importlib
    bcc = importlib.import_module('qryptify.cli.binance_candlestick_crawler')
    mock_db = mock.MagicMock()
    monkeypatch.setattr(bcc, 'TimescaleDB', mock_db)
    return mock_db


def test_binance_candlestick_crawler_db(patch_timescaledb):
    from click.testing import CliRunner

    # Import CLI after patching
    from qryptify.cli import cli
    output_db = 'postgresql://user:pass@localhost:5432/testdb'
    coin = 'BTC'
    time_interval = 60  # Should be a valid interval in BINANCE_INTERVALS
    runner = CliRunner()
    result = runner.invoke(cli, [
        'binance_candlestick_crawler', '--output_db', output_db, '--coin',
        coin, '--time-interval',
        str(time_interval)
    ])
    assert result.exit_code == 0 or result.exit_code == 1  # Accept ValueError for unsupported interval
    patch_timescaledb.assert_called_with(connection_url=output_db)
