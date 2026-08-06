# Phase 1 Data Requirements

## Objective

Establish a trusted, deterministic data foundation before introducing AI models. Phase 1 must answer: what equipment exists, what maintenance is due, what faults occurred, what repairs are open, who can service equipment, where service can occur, when equipment is available, what campaigns apply, and whether compliance records are current.

## Canonical datasets

| Dataset | Grain | Primary key | Purpose |
|---|---|---|---|
| equipment_master | one row/equipment | equipment_id | Fleet identity and current state |
| pm_schedule | one PM event/equipment | pm_id | Due dates, intervals, scheduling |
| maintenance_history | one completed maintenance event | maintenance_id | Historical repairs and PM outcomes |
| fault_events | one detected fault | fault_id | Fault history and severity |
| work_orders | one work order | work_order_id | Repair lifecycle and financial tracking |
| vendor_master | one vendor | vendor_id | Vendor identity, preferences and capabilities |
| service_locations | one service location | location_id | Location capability and availability |
| equipment_availability | one availability interval/equipment | availability_id | Operational scheduling windows |
| campaigns | one campaign | campaign_id | OEM campaign/recall/update applicability |
| compliance_inspections | one inspection | inspection_id | Compliance and inspection status |

## Required source attributes

### equipment_master

Equipment ID, unit number, VIN, equipment type, make, model, model year, engine type, in-service date, current mileage, engine hours, current location, operational status, ownership/lease status, home terminal, and last synchronization timestamp.

### pm_schedule

PM ID, equipment ID, PM type, due date, due mileage, due engine hours, interval rules, last completion date, last completion mileage, scheduled date, service location, vendor, status, and source timestamp.

### maintenance_history

Maintenance ID, equipment ID, work order ID, service date, maintenance type, complaint, cause, correction, parts, labor hours, labor rate, SRT, total cost, warranty indicator, vendor, location, mileage, and return-to-service timestamp.

### fault_events

Fault ID, equipment ID, source system, source fault code, normalized fault code, description, severity, safety flag, first detected, last detected, occurrence count, active/cleared state, mileage, engine hours, and resolution linkage.

### work_orders

Work order ID, equipment ID, opened date, status, priority, complaint, diagnosis, repair plan, vendor, location, estimate ID, estimated cost, approved cost, actual cost, approval status, warranty status, opened/closed timestamps, delay reason, and return-to-service status.

### vendor_master

Vendor ID, name, account type, preferred flag, supported equipment types, capabilities, labor rate, SRT agreement, national account, warranty handling capability, service hours, geographic coverage, contact channel, and active status.

### service_locations

Location ID, vendor ID, address/region, service capabilities, equipment capabilities, hours, appointment capacity, emergency capability, preferred flag, and active status.

### equipment_availability

Availability ID, equipment ID, start/end timestamp, availability type, route/assignment reference, operational constraints, and source timestamp.

### campaigns

Campaign ID, OEM, campaign/recall number, description, affected equipment criteria, effective date, expiration date, required action, safety criticality, completion status, and source document reference.

### compliance_inspections

Inspection ID, equipment ID, inspection type, inspection date, expiration/due date, result, defects, corrective action, compliance status, inspector/source, documentation reference, and timestamp.

## Data relationships

```text
equipment_master
    ├── pm_schedule
    ├── maintenance_history
    ├── fault_events
    ├── work_orders
    ├── equipment_availability
    ├── campaigns (through applicability rules)
    └── compliance_inspections

vendor_master
    ├── service_locations
    ├── work_orders
    └── maintenance_history
```

## Data quality rules

1. IDs must be non-null and unique within their dataset.
2. Foreign keys must resolve to canonical entities.
3. VIN format and equipment identity must be validated where available.
4. Dates must be valid and logically ordered.
5. PM due date cannot be earlier than last completion date unless an explicit exception exists.
6. Work-order closed time cannot precede opened time.
7. Actual cost cannot be negative.
8. Labor hours/rates and parts amounts must be non-negative.
9. Equipment must not have contradictory active statuses from the same source timestamp.
10. Duplicate source events must be detectable and idempotently handled.
11. Required safety/compliance fields cannot silently default to safe values.
12. Every source record must carry source system and ingestion timestamp.

## Data lifecycle

```text
Source systems / files
        -> raw
        -> validated
        -> standardized
        -> canonical
        -> curated analytical datasets
        -> Phase 1 deterministic rules
```

AI is explicitly out of scope for this phase.

## Phase 1 acceptance criteria

- All ten canonical datasets have schemas and data dictionaries.
- Synthetic data covers normal, missing, duplicate, invalid, stale, and conflicting cases.
- Referential integrity is validated.
- Data-quality checks produce machine-readable results.
- PM, fault, and work-order business rules operate only on validated data.
- Every dataset includes source and ingestion metadata.
- Re-running ingestion does not duplicate records.
- A Phase 1 readiness report can identify whether data is safe for downstream AI work.
