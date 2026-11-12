import json, uuid
from datetime import datetime, timezone
from pathlib import Path
from .ingestion import read_records
from .validation import validate
from .database import connect, ensure_table, publish


def run_pipeline(config_path, db_path="data/output/warehouse.db"):
    from .config import load_config
    cfg = load_config(config_path)
    run_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()
    source = cfg["source"]["path"]
    records = read_records(source, cfg["source"]["format"])
    con = connect(db_path)
    ensure_table(con, cfg)
    accepted, rejects, seen = 0, [], set()
    try:
        for i, record in enumerate(records, 1):
            clean, errors = validate(record, cfg)
            key = tuple(clean.get(k) for k in cfg["keys"])
            if not errors and key in seen: errors.append("duplicate_key_in_batch")
            if not errors and cfg.get("foreign_keys"):
                for field, ref in cfg["foreign_keys"].items():
                    table, column = ref.split(".")
                    found = con.execute(f'SELECT 1 FROM "{table}" WHERE "{column}"=?', (clean[field],)).fetchone()
                    if not found: errors.append(f"{field}: invalid_reference")
            if errors:
                rejects.append((run_id, source, i, json.dumps(record), "; ".join(errors)))
            else:
                seen.add(key)
                publish(con, cfg, clean)
                accepted += 1
        con.executemany("INSERT INTO rejects VALUES (?,?,?,?,?)", rejects)
        ended = datetime.now(timezone.utc).isoformat()
        con.execute("INSERT INTO pipeline_runs VALUES (?,?,?,?,?,?,?,?,?)", (run_id, cfg["name"], "success", len(records), accepted, len(rejects), started, ended, None))
        con.commit()
    except Exception as exc:
        con.rollback()
        ended = datetime.now(timezone.utc).isoformat()
        con.execute("INSERT INTO pipeline_runs VALUES (?,?,?,?,?,?,?,?,?)", (run_id, cfg["name"], "failed", len(records), accepted, len(rejects), started, ended, str(exc)))
        con.commit()
        raise
    finally:
        con.close()
    return {"run_id": run_id, "input": len(records), "loaded": accepted, "rejected": len(rejects), "status": "success"}
