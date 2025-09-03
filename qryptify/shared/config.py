from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .config_model import cfg_model_from_dict
from .config_model import validate_cfg_dict

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


def load_cfg_validated(path: str | Path = DEFAULT_CFG_PATH) -> Dict[str, Any]:
    """Load YAML config and validate basic invariants.

    Returns the raw dict (backwards compatibility) after validation.
    Raises ValueError on invalid configuration.
    """
    cfg = load_cfg(path)
    validate_cfg_dict(cfg)
    return cfg


def load_cfg_model(path: str | Path = DEFAULT_CFG_PATH):
    """Load YAML config and return a typed model (dataclasses).

    Backwards-compat functions still return dicts; callers may opt into this
    typed model if desired.
    """
    cfg = load_cfg(path)
    return cfg_model_from_dict(cfg)
