import sqlite3
from pathlib import Path


def connect(path):
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("CREATE TABLE IF NOT EXISTS pipeline_runs (run_id TEXT PRIMARY KEY, dataset TEXT, status TEXT, input_count INTEGER, output_count INTEGER, rejected_count INTEGER, started_at TEXT, ended_at TEXT, error TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS rejects (run_id TEXT, source_file TEXT, row_number INTEGER, record_json TEXT, errors TEXT)")
    return con


def ensure_table(con, cfg):
    table = cfg["target"]["table"]
    cols = []
    for name, spec in cfg["schema"].items():
        sqltype = "INTEGER" if spec["type"] == "integer" else "REAL" if spec["type"] == "number" else "TEXT"
        cols.append(f'"{name}" {sqltype}')
    keys = ",".join(f'"{k}"' for k in cfg["keys"])
    con.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(cols)}, PRIMARY KEY ({keys}))')


def publish(con, cfg, row):
    table = cfg["target"]["table"]
    fields = list(cfg["schema"])
    cols = ",".join(f'"{x}"' for x in fields)
    marks = ",".join("?" for _ in fields)
    if cfg["target"]["load_mode"] == "upsert":
        keys = set(cfg["keys"])
        updates = ",".join(f'"{x}"=excluded."{x}"' for x in fields if x not in keys)
        sql = f'INSERT INTO "{table}" ({cols}) VALUES ({marks}) ON CONFLICT ({",".join(cfg["keys"])}) DO UPDATE SET {updates}' if updates else f'INSERT OR IGNORE INTO "{table}" ({cols}) VALUES ({marks})'
    else:
        sql = f'INSERT INTO "{table}" ({cols}) VALUES ({marks})'
    con.execute(sql, [row.get(x) for x in fields])
