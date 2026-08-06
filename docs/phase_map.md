# Fleet Maintenance Data Map — Phases 1 to 6

This is the target data roadmap. Only Phase 1 datasets are populated on this branch.

| Phase | Business capability | Core datasets |
|---|---|---|
| 1 | Data foundation + deterministic maintenance control | equipment, PM, maintenance history, faults, work orders, vendors, service locations, availability, campaigns, compliance inspections |
| 2 | Driver/vendor communication + document intake | driver emails, voicemail transcripts, driver requests, vendor estimates, repair notes, invoices, communication metadata |
| 3 | RAG + maintenance intelligence | OEM manuals, service bulletins, campaigns/recalls, company policies, FMCSA guidance, vendor agreements, SRT, VMRS, warranty policies, repair procedures |
| 4 | Scheduling + workflow automation | vendor capacity, appointment slots, routes, dispatch commitments, travel time, service duration, approval thresholds, notification/audit events |
| 5 | Predictive maintenance | high-frequency ELD/telematics, mileage/engine hours history, fault sequences, repair outcomes, parts history, component lifecycle, weather/route context where permitted |
| 6 | Enterprise production optimization | model predictions/labels, feedback/override data, cost outcomes, vendor performance, warranty recovery, downtime, breakdown outcomes, compliance outcomes, full audit trail |

## Phase-gating principle

A later phase may consume earlier phase curated data, but it must not bypass the data-quality layer. Every new source needs a source contract, ownership, identifier mapping, freshness expectation, quality rules, and lineage.
