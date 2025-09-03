from __future__ import annotations

import sys
from typing import Optional

from loguru import logger


def setup_logging(level: str = "INFO", *, colorize: Optional[bool] = None) -> None:
    """Configure loguru with a consistent format across tools.

    Call once early in CLIs/services. Safe to call multiple times; it resets sinks.
    """
    logger.remove()
    fmt = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
           "| <level>{level: <8}</level> "
           "| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>")
    logger.add(sys.stderr, level=level.upper(), format=fmt, colorize=colorize)
