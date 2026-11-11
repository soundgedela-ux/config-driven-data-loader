import argparse
from src.pipeline import run_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration-driven data loader")
    parser.add_argument("config", help="YAML configuration file")
    parser.add_argument("--db", default="data/output/warehouse.db")
    args = parser.parse_args()
    print(run_pipeline(args.config, args.db))
