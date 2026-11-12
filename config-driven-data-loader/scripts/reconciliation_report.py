import sqlite3
from pathlib import Path


def print_report(db_path: str = "data/output/warehouse.db") -> None:
    db = Path(db_path)
    if not db.exists():
        print(f"Database not found at {db_path}")
        return

    con = sqlite3.connect(db)
    try:
        tables = ["customers", "orders"]
        print("Reconciliation report")
        print("=" * 24)
        for table in tables:
            row = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()
            print(f"{table}: {row[0] if row else 0} rows")

        rejected = con.execute("SELECT COUNT(*) FROM rejects").fetchone()[0]
        runs = con.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0]
        print(f"rejects: {rejected} rows")
        print(f"pipeline_runs: {runs} entries")

        latest = con.execute(
            "SELECT dataset, status, input_count, output_count, rejected_count FROM pipeline_runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        if latest:
            print(f"latest_run: dataset={latest[0]}, status={latest[1]}, input={latest[2]}, output={latest[3]}, rejected={latest[4]}")
    finally:
        con.close()


if __name__ == "__main__":
    print_report()
