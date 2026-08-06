# Phase 1 — Data Foundation

## Goal

Before introducing AI/ML models, establish a reliable, analyzable fleet-maintenance dataset and a repeatable data-quality process.

Phase 1 is intentionally **AI-free**. The output is trusted structured data plus deterministic rules that can later feed AI models.

## 1. What is input data?

Input data means every source needed to understand the maintenance state of an equipment unit and make a safe maintenance-priority decision.

For Phase 1, the minimum domains are:

1. **Equipment master** — what assets exist and their current identity/status.
2. **PM schedule** — what maintenance is due and when.
3. **Maintenance history** — what has already been repaired/serviced.
4. **Fault events** — what equipment faults are occurring and how often.
5. **Work orders** — what work is currently open, approved, delayed, or completed.
6. **Vendor master/preferences** — which vendors/locations are preferred and capable.
7. **Service locations** — where an asset can be serviced and location attributes.
8. **Equipment availability/operations** — when equipment can be taken out of service.
9. **Campaign/recall records** — applicable equipment campaigns that can create maintenance work.
10. **Compliance/inspection records** — safety/compliance events that affect priority and dispatch status.

Driver communications, vendor estimates/invoices, warranty documents, OEM documents, and richer ELD telemetry are required in later phases. Phase 1 should define their contracts now but not require them for the first deterministic priority engine.

## 2. Phase 1 source-to-purpose map

| Dataset | Purpose | Required? | Primary keys |
|---|---|---:|---|
| equipment_master | Asset identity/status | Yes | equipment_id, VIN |
| pm_schedule | PM due-date monitoring | Yes | pm_id, equipment_id |
| maintenance_history | Previous repairs and repeat failures | Yes | history_id, equipment_id |
| fault_events | Fault severity/repetition | Yes | fault_id, equipment_id |
| work_orders | Active maintenance workload | Yes | work_order_id, equipment_id |
| vendor_master | Vendor capabilities/preferences | Yes | vendor_id |
| service_locations | Location/service capacity | Yes | location_id |
| equipment_availability | Scheduling constraints | Yes | availability_id, equipment_id |
| campaigns | Recall/campaign applicability | Yes | campaign_id |
| compliance_inspections | Safety/compliance context | Yes | inspection_id, equipment_id |
| driver_requests | Maintenance intake | Phase 2 | request_id |
| vendor_estimates | Estimate validation | Phase 2 | estimate_id, work_order_id |
| invoices | Invoice validation | Phase 2 | invoice_id, work_order_id |
| warranty_events | Warranty recovery | Phase 2 | warranty_id, work_order_id |
| oem_documents | RAG knowledge | Phase 3 | document_id |
| ELD_telemetry | Advanced usage/failure features | Phase 3+ | event_id, equipment_id |

## 3. Canonical identifiers

Do not join datasets on unit number alone. Phase 1 must establish stable identifiers:

```text
equipment_id       canonical internal asset key
vin                immutable vehicle identity where applicable
unit_number        operational/display identifier
pm_id              PM event/task key
fault_id           fault event key
work_order_id      maintenance transaction key
vendor_id          vendor key
location_id        service-location key
campaign_id        campaign/recall key
inspection_id      compliance/inspection key
```

All source-system IDs should be retained as `source_system` + `source_record_id` for traceability.

## 4. Required data fields

### equipment_master

```text
equipment_id
unit_number
vin
asset_type
make
model
year
engine_model
status
current_location_id
current_mileage
engine_hours
in_service_date
retirement_date
criticality_class
source_system
source_record_id
updated_at
```

### pm_schedule

```text
pm_id
equipment_id
pm_type
interval_miles
interval_days
last_service_date
last_service_mileage
current_due_date
current_due_mileage
scheduled_date
status
required_by_oem
required_by_company_policy
source_system
source_record_id
updated_at
```

### maintenance_history

```text
history_id
equipment_id
work_order_id
service_date
repair_category
component
fault_code
repair_description
parts_cost
labor_cost
total_cost
vendor_id
warranty_flag
repeat_repair_flag
mileage_at_service
engine_hours_at_service
source_system
source_record_id
```

### fault_events

```text
fault_id
equipment_id
fault_code
fault_source
first_detected_at
last_detected_at
occurrence_count
severity
safety_related
compliance_related
active_flag
odometer
engine_hours
raw_description
normalized_description
source_system
source_record_id
```

### work_orders

```text
work_order_id
equipment_id
opened_at
status
work_type
priority
problem_description
repair_description
vendor_id
service_location_id
estimated_cost
approved_cost
actual_cost
approval_status
safety_hold
compliance_hold
completion_at
last_updated_at
closed_at
delay_reason
source_system
source_record_id
```

### vendor_master

```text
vendor_id
vendor_name
vendor_type
status
preferred_flag
national_account_flag
supported_asset_types
supported_services
labor_rate
standard_srt_source
warranty_capability
contact_reference
source_system
source_record_id
```

### service_locations

```text
location_id
vendor_id
location_name
address
city
state
latitude
longitude
service_hours
capacity_per_day
supported_services
supported_asset_types
preferred_flag
active_flag
```

### equipment_availability

```text
availability_id
equipment_id
start_at
end_at
availability_status
operational_commitment
route_reference
planned_dispatch
planned_downtime
```

### campaigns

```text
campaign_id
campaign_type
campaign_number
oem
campaign_description
applicable_make
applicable_model
applicable_year_from
applicable_year_to
applicability_rule
severity
due_date
status
source_reference
```

### compliance_inspections

```text
inspection_id
equipment_id
inspection_type
inspection_date
inspection_status
finding_code
finding_description
safety_related
compliance_related
corrective_action_required
resolved_at
source_system
source_record_id
```

## 5. Data pipeline

```text
Source Systems
    |
    v
Landing / Raw
    |
    v
Schema Validation
    |
    v
Standardization
    |
    v
Deduplication
    |
    v
Entity Resolution
    |
    v
Business Validation
    |
    v
Canonical Data Model
    |
    +--> Data Quality Metrics
    |
    +--> Phase 1 Rules Engine
    |
    +--> Curated Dataset for Phase 2+
```

Raw data must remain immutable. Transformations should be reproducible and versioned.

## 6. Data-quality checks

### Completeness

- Every active equipment record has `equipment_id` and a valid identity.
- PM records have equipment, due date, and status.
- Fault events have equipment, code, and detection timestamp.
- Work orders have equipment and opened timestamp.

### Validity

- Dates/timestamps are parseable and timezone-aware.
- Mileage and cost fields are non-negative unless a documented correction exists.
- Status and priority values are controlled enums.
- VIN format is validated where VIN exists.

### Consistency

- Every PM equipment_id exists in equipment_master.
- Every fault equipment_id exists in equipment_master.
- Every work-order equipment_id exists in equipment_master.
- Vendor and service-location references resolve.
- Closed work orders cannot have a future completion date.
- Completed PMs must have a service date.

### Uniqueness

- Source record IDs are unique per source system.
- No duplicate active PM task for the same PM key.
- No duplicate fault event ingestion.

### Temporal integrity

- `opened_at <= completion_at <= closed_at` when all exist.
- `last_service_date <= current_due_date` for normal PM cycles.
- A work order cannot be closed before it is opened.

## 7. Phase 1 deterministic outputs

Once data passes quality checks, generate:

1. PM due-soon alerts.
2. Overdue PM alerts.
3. Active safety/compliance alerts.
4. Fault-priority alerts.
5. Repeat-repair indicators.
6. Work orders older than 30 days.
7. Equipment maintenance priority queue.
8. Daily data-quality report.

## 8. Phase 1 does not train AI models

Do not start with an LLM or predictive model. First prove that the source data can consistently answer:

- Which equipment exists?
- What is due and when?
- What faults are active?
- What repairs happened previously?
- What work is currently open?
- Which equipment is unavailable?
- Which vendors/locations are eligible?
- Which safety/compliance conditions require escalation?

Only after these questions are reliably answerable should AI models be introduced.

## 9. Definition of Done

Phase 1 data foundation is complete when:

- All nine required Phase 1 datasets have schemas/contracts.
- Synthetic data covers normal, overdue, missing, duplicate, and conflicting cases.
- Data validation produces a measurable quality report.
- Canonical IDs support joins across datasets.
- Raw and curated layers are separated.
- Deterministic PM/fault/work-order rules run only on validated curated data.
- Every curated record can be traced back to a source record.
- Tests cover data-quality rules and business rules.
- No proprietary production data is committed to GitHub.
