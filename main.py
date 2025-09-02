import asyncio

from loguru import logger

from qryptify.shared.config import load_cfg
from qryptify_ingestor.coordinator import run_all

if __name__ == "__main__":
    cfg = load_cfg()
    pairs = cfg.get("pairs")
    logger.info(f"Starting Qryptify Ingestor | pairs={pairs}")
    asyncio.run(run_all(cfg))
