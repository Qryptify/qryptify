import asyncio

import yaml

from qryptify_ingestor.coordinator import run_all


def load_cfg():
    with open("qryptify_ingestor/config.yaml", "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    cfg = load_cfg()
    asyncio.run(run_all(cfg))
