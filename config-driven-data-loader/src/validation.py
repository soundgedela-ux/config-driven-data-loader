from datetime import datetime
import re


def validate(record, cfg):
    errors, cleaned = [], {}
    schema = cfg["schema"]
    if set(record) != set(schema):
        errors.append("schema_mismatch")
    for field, spec in schema.items():
        value = record.get(field)
        if value in (None, ""):
            if not spec.get("nullable", True): errors.append(f"{field}: required")
            cleaned[field] = None
            continue
        typ = spec["type"]
        try:
            if typ == "integer": value = int(value)
            elif typ == "number": value = float(value)
            elif typ == "string": value = str(value).strip()
            elif typ == "datetime":
                value = datetime.fromisoformat(str(value).replace("Z", "+00:00")).isoformat()
            else: errors.append(f"{field}: unsupported type {typ}")
        except (ValueError, TypeError): errors.append(f"{field}: invalid {typ}")
        cleaned[field] = value
    if cfg.get("rules", {}).get("email") and cleaned.get("email") and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cleaned["email"]):
        errors.append("email: invalid")
    minimum = cfg.get("rules", {}).get("amount_min")
    if minimum is not None and cleaned.get("amount") is not None and cleaned["amount"] < minimum:
        errors.append("amount: below minimum")
    return cleaned, errors
