from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Union

from .intervals import SUPPORTED_INTERVALS


@dataclass
class PairSpec:
    symbol: str
    interval: str


@dataclass
class RESTConfig:
    endpoint: str
    klines_limit: int = 1500


@dataclass
class WSConfig:
    endpoint: str


@dataclass
class DBConfig:
    dsn: str


@dataclass
class BackfillConfig:
    start_date: str


@dataclass
class IngestorConfig:
    pairs: List[PairSpec]
    rest: RESTConfig
    ws: WSConfig
    db: DBConfig
    backfill: BackfillConfig
    live: Optional[dict] = None


def _parse_pair(item: Union[str, dict[str, Any]]) -> PairSpec:
    if isinstance(item, str):
        s = item.strip()
        if "/" in s:
            sym, itv = s.split("/", 1)
        elif "-" in s:
            sym, itv = s.split("-", 1)
        else:
            raise ValueError(f"Invalid pair format '{item}'")
        return PairSpec(symbol=sym.strip().upper(), interval=itv.strip())
    if isinstance(item, dict):
        sym = str(item.get("symbol", "")).strip().upper()
        itv = str(item.get("interval", "")).strip()
        if not sym or not itv:
            raise ValueError(
                "Invalid pair object; expected keys 'symbol' and 'interval'")
        return PairSpec(symbol=sym, interval=itv)
    raise ValueError(f"Unsupported pair entry: {item}")


def validate_cfg_dict(cfg: dict) -> None:
    # Basic structure
    for key in ("pairs", "rest", "ws", "db", "backfill"):
        if key not in cfg:
            raise ValueError(f"config missing key: {key}")
    # Pairs
    pairs = cfg.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        raise ValueError("config.pairs must be a non-empty list")
    for p in pairs:
        ps = _parse_pair(p)
        if ps.interval not in SUPPORTED_INTERVALS:
            raise ValueError(f"Unsupported interval: {ps.interval}")
    # DB
    dsn = cfg.get("db", {}).get("dsn")
    if not isinstance(dsn, str) or not dsn.strip():
        raise ValueError("config.db.dsn must be a non-empty string")
    # Endpoints
    rest_ep = cfg.get("rest", {}).get("endpoint")
    ws_ep = cfg.get("ws", {}).get("endpoint")
    if not isinstance(rest_ep, str) or not rest_ep.strip():
        raise ValueError("config.rest.endpoint must be set")
    if not isinstance(ws_ep, str) or not ws_ep.strip():
        raise ValueError("config.ws.endpoint must be set")
    # Backfill
    start_date = cfg.get("backfill", {}).get("start_date")
    if not isinstance(start_date, str) or not start_date.strip():
        raise ValueError("config.backfill.start_date must be set (ISO string)")


def cfg_model_from_dict(cfg: dict) -> IngestorConfig:
    validate_cfg_dict(cfg)
    pairs = [_parse_pair(p) for p in cfg["pairs"]]
    rest = RESTConfig(
        endpoint=str(cfg["rest"]["endpoint"]).strip(),
        klines_limit=int(cfg["rest"].get("klines_limit", 1500)),
    )
    ws = WSConfig(endpoint=str(cfg["ws"]["endpoint"]).strip())
    db = DBConfig(dsn=str(cfg["db"]["dsn"]).strip())
    backfill = BackfillConfig(start_date=str(cfg["backfill"]["start_date"]).strip())
    live = cfg.get("live") if isinstance(cfg.get("live"), dict) else None
    return IngestorConfig(pairs=pairs,
                          rest=rest,
                          ws=ws,
                          db=db,
                          backfill=backfill,
                          live=live)
