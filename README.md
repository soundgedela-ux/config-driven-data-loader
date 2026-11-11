# Configuration-driven Data Loader

A local Python + SQLite data pipeline. Dataset-specific source path, format, schema, keys, target table and load mode are declared in YAML rather than embedded in pipeline code.

## Architecture

`YAML config -> CSV/JSON ingestion -> schema/type/business validation -> duplicate and FK checks -> SQLite target + reject log + run metrics`

## Requirements and setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py
```

## Run

```bash
python main.py config/customers.yaml
python main.py config/orders.yaml
```

Run customers before orders because orders reference customer IDs. The database is written to `data/output/warehouse.db`.

## Tests

```bash
pytest -q
```

## Scale and reproducibility

The generator accepts `--customers`, `--orders`, and `--seed`; e.g. `python scripts/generate_data.py --customers 100000 --orders 300000 --seed 42`.

## Conventions and assumptions

- Tables and columns use snake_case.
- IDs are stable source-provided integer keys; no random target IDs are generated.
- Timestamps use ISO-8601 strings.
- Each run receives a UUID `run_id`; rejects record `source_file` and row number.
- `upsert` makes rerunning the same keys safe. `append` is available for append-only datasets and requires unique keys.
- Orders are checked against the customers target table; load customers first.
- Invalid records are recorded in `rejects`; run metrics are stored in `pipeline_runs`.

## Limitations / next steps

This is a compact assessment implementation. It uses local SQLite and file inputs; production deployments could add object storage, API connectors, schema versioning, stronger type coercion, structured logging, batch processing, and recovery checkpoints. The current sample tests cover a successful load and idempotent rerun; expand tests for malformed input, nulls, schema drift, FK failures, and partial failures before production use.
