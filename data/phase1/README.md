# Phase 1 Synthetic Data

These CSV files are synthetic and contain no production fleet information.

## Load order

1. equipment_master
2. vendor_master
3. service_locations
4. pm_schedule
5. maintenance_history
6. fault_events
7. work_orders
8. equipment_availability
9. campaigns
10. compliance_inspections

## Why these datasets?

Together they answer the Phase 1 operational questions:

- What assets exist and where are they?
- Which PMs are due, overdue, or already scheduled?
- What repairs happened previously?
- Which faults are active, repeated, safety-related, or compliance-related?
- Which work orders are open and how old are they?
- Which vendors and service locations are eligible/preferred?
- When can equipment be removed from service?
- Are campaigns/recalls applicable?
- Are there safety/compliance findings that change priority?

## Production ingestion rule

Never commit real TMT, ELD, OEM, PFJ, driver, vendor, or employee data to this repository. Production data must enter through authenticated integrations into controlled raw storage.
