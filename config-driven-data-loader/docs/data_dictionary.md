# Data dictionary

## customers
- Grain: one row per customer.
- `customer_id`: integer primary key, required.
- `customer_name`: required string.
- `email`: required string; basic email format check.

## orders
- Grain: one row per order.
- `order_id`: integer primary key, required.
- `customer_id`: required FK to `customers.customer_id`.
- `amount`: required number, minimum 0.
- `order_date`: required ISO-8601 datetime.

Operational tables: `pipeline_runs` stores run status and counts; `rejects` stores source file, row number, original record and validation errors.
