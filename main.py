import asyncio

from loguru import logger

from qryptify.shared.config import load_cfg_validated
from qryptify.shared.logging import setup_logging
from qryptify_ingestor.coordinator import run_all


def main() -> None:
    setup_logging("INFO")
    cfg = load_cfg_validated()
    pairs = cfg.get("pairs")
    logger.info(f"Starting Qryptify Ingestor | pairs={pairs}")
    asyncio.run(run_all(cfg))


if __name__ == "__main__":
    main()
