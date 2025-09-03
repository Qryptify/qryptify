from __future__ import annotations

import pytest

from qryptify.shared.config_model import validate_cfg_dict
from qryptify.shared.pairs import parse_pair
from qryptify.shared.pairs import symbol_interval_pairs_from_cfg


def test_parse_pair_formats():
    assert parse_pair("BTCUSDT/1h") == ("BTCUSDT", "1h")
    assert parse_pair("ethusdt-4h") == ("ETHUSDT", "4h")
    with pytest.raises(ValueError):
        parse_pair("")
    with pytest.raises(ValueError):
        parse_pair("BTCUSDT")


def test_symbol_interval_pairs_from_cfg_mixed_and_dedup():
    cfg = {
        "pairs": [
            "BTCUSDT/1h",
            "ETHUSDT-4h",
            {
                "symbol": "BNBUSDT",
                "interval": "15m"
            },
            "BTCUSDT/1h",  # duplicate
        ]
    }
    out = symbol_interval_pairs_from_cfg(cfg)
    assert out == [("BTCUSDT", "1h"), ("ETHUSDT", "4h"), ("BNBUSDT", "15m")]


def test_validate_cfg_dict_happy_path():
    cfg = {
        "pairs": ["BTCUSDT/1h"],
        "rest": {
            "endpoint": "https://fapi.binance.com",
            "klines_limit": 1500
        },
        "ws": {
            "endpoint": "wss://fstream.binance.com/stream"
        },
        "db": {
            "dsn": "postgresql://postgres:postgres@localhost:5432/qryptify"
        },
        "backfill": {
            "start_date": "2022-01-01T00:00:00Z"
        },
    }
    validate_cfg_dict(cfg)  # should not raise


def test_validate_cfg_dict_invalid_interval():
    cfg = {
        "pairs": ["BTCUSDT/7m"],
        "rest": {
            "endpoint": "x"
        },
        "ws": {
            "endpoint": "y"
        },
        "db": {
            "dsn": "z"
        },
        "backfill": {
            "start_date": "2022-01-01T00:00:00Z"
        },
    }
    with pytest.raises(ValueError):
        validate_cfg_dict(cfg)
