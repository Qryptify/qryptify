"""Backwards-compatible re-exports for pair parsing utilities.

This module now delegates to qryptify.shared.pairs to keep imports stable
for one release cycle.
"""

from __future__ import annotations

from typing import List, Tuple

from qryptify.shared.pairs import parse_pair as _parse_pair
from qryptify.shared.pairs import symbol_interval_pairs_from_cfg as _pairs_from_cfg


def parse_pair(pair: str) -> tuple[str, str]:
    """Parse a single pair string into (SYMBOL, interval)."""
    return _parse_pair(pair)


def symbol_interval_pairs_from_cfg(cfg) -> List[Tuple[str, str]]:
    """Return list of (symbol, interval) pairs from cfg['pairs'] only."""
    return _pairs_from_cfg(cfg)
