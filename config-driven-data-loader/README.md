# Configuration-driven Data Loader

A local Python + SQLite data pipeline. Dataset-specific source path, format, schema, keys, target table, and load mode are declared in YAML rather than embedded in the pipeline code.

## Architecture

`YAML config -> CSV/JSON ingestion -> schema/type/business validation -> duplicate and FK checks -> SQLite target + reject log + run metrics`

## Data model and assumptions

- Tables and columns use snake_case.
- Customer IDs and order IDs are stable source-provided integer keys.
- Timestamps use ISO-8601 strings.
- Each run receives a UUID `run_id`; rejects record `source_file` and row number.
- `upsert` makes rerunning the same keys safe. `append` is available for append-only datasets and requires unique keys.
- Orders are checked against the `customers` target table; load customers before orders.
- Invalid records are recorded in `rejects`; run metrics are stored in `pipeline_runs`.
- Empty batches are treated as successful zero-row runs, while malformed rows are rejected without breaking the rest of the batch.

## Requirements and setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py
```

## Run the pipeline

```bash
python main.py config/customers.yaml
python main.py config/orders.yaml
```

The default output database is `data/output/warehouse.db` and the loader creates parent directories automatically if they do not exist.

## Reproducible sample and larger dataset

```bash
python scripts/generate_data.py --customers 100 --orders 500 --seed 42
python scripts/generate_data.py --customers 100000 --orders 300000 --seed 42
```

## Automated tests and validation evidence

```bash
python -m pytest -q
```

The suite checks:
- successful load and rerun safety
- missing output directory creation
- malformed records and duplicate keys
- empty batch behavior
- invalid foreign key rejection

## Reconciliation and operational report

```bash
python scripts/reconciliation_report.py
```

This script connects to the SQLite warehouse, prints key counts for each table, and confirms that the number of loaded rows matches the accepted rows in the target tables.

## Performance check

```bash
python scripts/performance_check.py --customers 5000 --orders 15000 --seed 42
```

This produces a simple runtime benchmark and identifies the dominant cost in the pipeline. A reasonable optimization is to batch inserts or switch to a bulk-loading path for very large files, while keeping the config-driven validation layer unchanged.

## Limits and trade-offs

This is a compact assessment implementation built for local, file-based ETL. It uses local SQLite and straightforward validation to keep the solution easy to run and test. Production enhancements could include partitioning, streaming ingestion, stronger schema enforcement, richer logging, and cloud-based storage.
