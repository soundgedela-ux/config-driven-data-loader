import csv, json
from pathlib import Path


def read_records(path, fmt):
    path = Path(path)
    if fmt == "csv":
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    if fmt == "json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON input must contain an array of records")
        return data
    raise ValueError(f"Unsupported format: {fmt}")
