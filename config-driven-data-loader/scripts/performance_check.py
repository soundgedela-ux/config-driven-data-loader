import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_command(args):
    subprocess.run(args, check=True)


def main():
    parser = argparse.ArgumentParser(description="Run a quick performance benchmark for the config-driven data loader.")
    parser.add_argument("--customers", type=int, default=5000)
    parser.add_argument("--orders", type=int, default=15000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--db", default="data/output/warehouse.db")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    generator = [
        sys.executable,
        str(root / "scripts" / "generate_data.py"),
        "--customers",
        str(args.customers),
        "--orders",
        str(args.orders),
        "--seed",
        str(args.seed),
    ]

    start = time.perf_counter()
    run_command(generator)
    run_command([sys.executable, str(root / "main.py"), "config/customers.yaml", "--db", args.db])
    run_command([sys.executable, str(root / "main.py"), "config/orders.yaml", "--db", args.db])
    elapsed = time.perf_counter() - start

    print(f"Generated {args.customers} customers and {args.orders} orders in {elapsed:.2f}s")
    print("Likely dominant cost: row validation and SQLite writes during batch processing.")
    print("Optimization: batch inserts / bulk writes while keeping validation logic unchanged.")


if __name__ == "__main__":
    main()
