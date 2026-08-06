# Phase 1 Data Quality Rules

## Dimensions

- Completeness: required fields populated.
- Uniqueness: canonical keys do not duplicate.
- Validity: values conform to type, range, enum, and format rules.
- Consistency: related datasets agree on shared entities and states.
- Timeliness: source updates arrive within expected freshness windows.
- Referential integrity: child records resolve to parent entities.
- Idempotency: repeated source delivery does not create duplicate canonical events.

## Severity

| Severity | Meaning | Action |
|---|---|---|
| ERROR | Unsafe or unusable record | Quarantine from curated data |
| WARNING | Usable with known limitation | Publish with quality flag |
| INFO | Informational observation | Record metric |

## Mandatory validation groups

### Identity

- equipment_id, pm_id, fault_id, work_order_id, vendor_id, location_id and inspection_id are non-empty.
- source_system and source_record_id are present.
- source_record_id is unique per source system and dataset.

### Date/time

- timestamps are parseable and timezone-aware where timestamp precision matters.
- end timestamps are not earlier than start timestamps.
- closed work orders cannot close before opening.
- PM completion cannot occur after a later conflicting completion event without an explicit correction record.

### Numeric

- mileage, engine hours, labor hours, rates and monetary amounts are non-negative.
- appointment capacity and occurrence counts are non-negative integers.

### Referential

- every equipment child record maps to equipment_master.
- vendor_id maps to an active/known vendor where required.
- location_id maps to service_locations where present.
- work-order and maintenance records reference valid equipment.

### Safety/compliance

- safety_related must be explicit for fault events.
- compliance status cannot default to compliant when source data is missing.
- campaign applicability must be traceable to equipment criteria and source evidence.

### Business rules

- PM due within five days without a scheduled service is an actionable event.
- overdue PM is a critical scheduling exception.
- work order older than 30 days requires a delay reason.
- repair cost changes above the configured approval threshold require explicit approval evidence.

## Quality output

Each validation run should produce:

```text
run_id
run_timestamp
dataset
source_system
rows_received
rows_valid
rows_warning
rows_error
completeness_score
validity_score
uniqueness_score
referential_integrity_score
freshness_status
quarantined_rows
```

A future implementation should persist these metrics so data quality trends can be monitored over time.
