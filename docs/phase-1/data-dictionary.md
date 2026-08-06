# Phase 1 Data Dictionary

The canonical model deliberately separates operational identity, maintenance, fault, vendor, availability, campaign, and compliance concerns.

## Common metadata

| Field | Type | Required | Description |
|---|---|---:|---|
| source_system | string | yes | Origin such as TMT, OEM, ELD, PFJ, vendor, file |
| source_record_id | string | yes | Stable source identifier |
| ingested_at | datetime | yes | Time record entered the platform |
| source_updated_at | datetime | no | Source last-update timestamp |

## equipment_master

| Field | Type | Required |
|---|---|---:|
| equipment_id | string | yes |
| unit_number | string | yes |
| vin | string | preferred |
| equipment_type | string | yes |
| make | string | yes |
| model | string | yes |
| model_year | integer | yes |
| in_service_date | date | no |
| current_mileage | integer | yes |
| engine_hours | decimal | no |
| current_location | string | no |
| operational_status | enum | yes |
| home_terminal | string | no |

## pm_schedule

| Field | Type | Required |
|---|---|---:|
| pm_id | string | yes |
| equipment_id | string | yes |
| pm_type | string | yes |
| due_date | date | yes |
| due_mileage | integer | no |
| due_engine_hours | decimal | no |
| last_completion_date | date | no |
| last_completion_mileage | integer | no |
| scheduled_date | date | no |
| vendor_id | string | no |
| location_id | string | no |
| status | enum | yes |

## fault_events

| Field | Type | Required |
|---|---|---:|
| fault_id | string | yes |
| equipment_id | string | yes |
| source_fault_code | string | yes |
| normalized_fault_code | string | no |
| description | string | no |
| severity | enum | yes |
| safety_related | boolean | yes |
| first_detected | datetime | yes |
| last_detected | datetime | no |
| occurrence_count | integer | yes |
| state | enum | yes |

## work_orders

| Field | Type | Required |
|---|---|---:|
| work_order_id | string | yes |
| equipment_id | string | yes |
| opened_at | datetime | yes |
| closed_at | datetime | no |
| status | enum | yes |
| priority | enum | yes |
| vendor_id | string | no |
| location_id | string | no |
| estimated_cost | decimal | yes |
| approved_cost | decimal | yes |
| actual_cost | decimal | yes |
| warranty_status | enum | yes |
| delay_reason | string | conditional |

## vendor_master

| Field | Type | Required |
|---|---|---:|
| vendor_id | string | yes |
| vendor_name | string | yes |
| preferred | boolean | yes |
| capabilities | array | yes |
| labor_rate | decimal | no |
| service_hours | string | no |
| geographic_coverage | array | no |
| active | boolean | yes |

## service_locations

| Field | Type | Required |
|---|---|---:|
| location_id | string | yes |
| vendor_id | string | yes |
| region | string | yes |
| capabilities | array | yes |
| appointment_capacity | integer | no |
| emergency_capable | boolean | yes |
| preferred | boolean | yes |
| active | boolean | yes |

## equipment_availability

| Field | Type | Required |
|---|---|---:|
| availability_id | string | yes |
| equipment_id | string | yes |
| start_at | datetime | yes |
| end_at | datetime | yes |
| availability_type | enum | yes |
| operational_constraint | string | no |

## campaigns

| Field | Type | Required |
|---|---|---:|
| campaign_id | string | yes |
| oem | string | yes |
| campaign_number | string | yes |
| description | string | yes |
| effective_date | date | no |
| required_action | string | yes |
| safety_critical | boolean | yes |
| source_document_ref | string | no |

## compliance_inspections

| Field | Type | Required |
|---|---|---:|
| inspection_id | string | yes |
| equipment_id | string | yes |
| inspection_type | string | yes |
| inspection_date | date | yes |
| due_date | date | no |
| result | enum | yes |
| defects | array | no |
| compliance_status | enum | yes |
| documentation_ref | string | no |
