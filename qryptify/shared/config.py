from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

DEFAULT_CFG_PATH = Path("qryptify_ingestor/config.yaml")


def load_cfg(path: str | Path = DEFAULT_CFG_PATH) -> Dict[str, Any]:
    """Load YAML config used by ingestor and strategy components.

    Defaults to qryptify_ingestor/config.yaml at repo root.
    """
    p = Path(path)
    with p.open("r") as f:
        return yaml.safe_load(f) or {}


def load_cfg_dsn(path: str | Path = DEFAULT_CFG_PATH) -> str:
    cfg = load_cfg(path)
    return cfg["db"]["dsn"]
