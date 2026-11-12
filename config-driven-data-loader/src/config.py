import yaml
from pathlib import Path


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if cfg["target"]["load_mode"] not in {"upsert", "append"}:
        raise ValueError("load_mode must be upsert or append")
    return cfg
