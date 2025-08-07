import os
import subprocess
import sys

import pytest

CLI_PATH = os.path.join(os.path.dirname(__file__), '..', 'qryptify', 'run.py')
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def test_cli_help():
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT
    result = subprocess.run([sys.executable, CLI_PATH, '--help'],
                            capture_output=True,
                            text=True,
                            env=env)
    assert result.returncode == 0
    assert 'Usage:' in result.stdout or 'Show this message' in result.stdout


def test_binance_candlestick_crawler_help():
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT
    result = subprocess.run(
        [sys.executable, CLI_PATH, 'binance_candlestick_crawler', '--help'],
        capture_output=True,
        text=True,
        env=env)
    assert result.returncode == 0
    assert 'Usage:' in result.stdout or 'Show this message' in result.stdout
