import asyncio

from loguru import logger
import yaml

from qryptify_ingestor.coordinator import run_all


def load_cfg() -> dict:
    """Load YAML config used by ingestor and strategy components."""
    with open("qryptify_ingestor/config.yaml", "r") as f:
        return yaml.safe_load(f) or {}


if __name__ == "__main__":
    cfg = load_cfg()
    pairs = cfg.get("pairs")
    logger.info(f"Starting Qryptify Ingestor | pairs={pairs}")
    asyncio.run(run_all(cfg))
