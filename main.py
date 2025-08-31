import asyncio

from loguru import logger
import yaml

from qryptify_ingestor.coordinator import run_all


def load_cfg():
    with open("qryptify_ingestor/config.yaml", "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    cfg = load_cfg()
    logger.info(
        f"Starting Qryptify Ingestor | symbols={cfg.get('symbols')} intervals={cfg.get('intervals')}"
    )
    asyncio.run(run_all(cfg))
