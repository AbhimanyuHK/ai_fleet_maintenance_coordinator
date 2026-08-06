# Phase 1 Data Layers

The project uses a simple medallion-style lifecycle while keeping the implementation technology-neutral.

```text
Source
  |
  v
RAW
  |  preserve source payload and metadata
  v
VALIDATED
  |  type, schema, quality and referential checks
  v
STANDARDIZED
  |  normalize dates, codes, units and enums
  v
CANONICAL
  |  common fleet-maintenance entities
  v
CURATED
  |  PM, fault, work-order and compliance views
  v
RULE ENGINE
```

## Raw

Preserve source meaning. Do not overwrite source values. Add ingestion metadata and a deterministic record fingerprint.

## Validated

Reject or quarantine records that violate mandatory contracts. Warnings remain traceable.

## Standardized

Normalize timezone handling, mileage units, money precision, enumerations, equipment identifiers, vendor identifiers, and fault-code representations.

## Canonical

Map source-specific structures to the canonical Phase 1 datasets defined in `data-requirements.md`.

## Curated

Build purpose-specific datasets such as:

- `pm_due_queue`
- `active_fault_queue`
- `open_work_order_queue`
- `equipment_maintenance_snapshot`
- `vendor_service_snapshot`
- `compliance_snapshot`

These curated datasets are the inputs to deterministic business rules and later AI features.

## Design principle

Do not send raw source data directly to an AI model. AI will consume governed, quality-checked, appropriately filtered data with source lineage and evidence references.
