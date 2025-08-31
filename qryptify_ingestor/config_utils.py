from __future__ import annotations

from typing import List, Tuple


def symbol_interval_pairs_from_cfg(cfg) -> List[Tuple[str, str]]:
    """Return list of (symbol, interval) pairs from cfg['pairs'] only.

    Supported formats per entry:
      - "SYMBOL/interval" (e.g., "BTCUSDT/1m")
      - "SYMBOL-interval" (e.g., "ETHUSDT-1h")
      - {symbol: SYMBOL, interval: INTERVAL}
    """
    pairs = cfg.get("pairs")
    if not pairs:
        raise ValueError(
            "config.yaml must define 'pairs' with symbol-interval entries")

    out: list[tuple[str, str]] = []
    for item in pairs:
        if isinstance(item, str):
            s = item.strip()
            if "/" in s:
                sym, itv = s.split("/", 1)
            elif "-" in s:
                sym, itv = s.split("-", 1)
            else:
                raise ValueError(
                    f"Invalid pair format '{s}'. Use SYMBOL/interval or SYMBOL-interval."
                )
            out.append((sym.strip().upper(), itv.strip()))
        elif isinstance(item, dict):
            sym = str(item.get("symbol", "")).strip().upper()
            itv = str(item.get("interval", "")).strip()
            if not sym or not itv:
                raise ValueError(
                    f"Invalid pair entry {item}; expected keys 'symbol' and 'interval'."
                )
            out.append((sym, itv))
        else:
            raise ValueError(
                f"Invalid pair entry type {type(item)}; expected str or {dict}"
            )
    # de-duplicate while preserving order
    seen = set()
    uniq: list[tuple[str, str]] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq
