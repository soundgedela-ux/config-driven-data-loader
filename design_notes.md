# Design notes

YAML metadata separates dataset-specific settings from reusable ingestion and validation logic. SQLite keeps the assessment runnable without cloud credentials. Upsert is the default for safe reruns. Invalid rows are quarantined with their original payload and reason. The trade-off is that SQLite is suitable for a local demonstration, not high-throughput distributed processing.
