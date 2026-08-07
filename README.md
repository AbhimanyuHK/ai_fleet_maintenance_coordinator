# AI Fleet Maintenance Coordinator

AI-powered Fleet Maintenance Operations Automation Platform.

## Vision

Reduce preventable breakdowns, improve fleet uptime and safety, reduce maintenance cost leakage, recover warranty value, and reduce manual coordination work.

## Phase 1 — Data Foundation ✅ COMPLETE

Phase 1 establishes the trusted data foundation required before introducing AI models.

### Canonical input datasets

- Equipment Master
- PM Schedule
- Maintenance History
- Fault Events
- Work Orders
- Vendor Master
- Service Locations
- Equipment Availability
- Campaigns / Recalls
- Compliance Inspections

### Phase 1 capabilities

- Canonical data requirements and data dictionary
- Source-system and ingestion lineage
- RAW → VALIDATED → STANDARDIZED → CANONICAL → CURATED data lifecycle
- Required-field and schema validation
- Duplicate and canonical-key detection
- Referential-integrity validation
- Date/time consistency validation
- Non-negative numeric validation
- Data-quality rules and reporting
- Data profiling and normalization
- Curated operational datasets for PMs, faults, work orders, equipment, vendors, and compliance
- Deterministic PM scheduling, fault prioritization, and work-order aging rules
- Phase 1 readiness gate
- Automated tests and GitHub Actions CI
- Synthetic datasets for development and demonstration
- Read-only Streamlit business data explorer

## Phase 2 — Operational Data Engineering ✅ COMPLETE

Phase 2 adds the operational inputs needed to understand communications, vendor repair activity, estimates, invoices, repair notes, and human-review requirements.

### Phase 2 datasets

- Driver requests
- Communication messages and participants
- Voicemail records
- Vendor estimates and estimate lines
- Vendor invoices and invoice lines
- Repair notes
- Document artifacts
- Human review tasks

### Phase 2 capabilities

- Communication and driver-request normalization
- Vendor estimate/invoice reconciliation
- Invoice variance detection
- Repair-document data extraction foundation
- Human review queue generation
- Data-quality validation and regression tests
- Streamlit operational-data views

## Phase 3 — Knowledge Foundation & AI Intelligence ✅ COMPLETE

Phase 3 introduces approved maintenance knowledge and grounded AI decision support while preserving human approval for operational actions.

### Phase 3 capabilities

- Approved OEM/company knowledge corpus
- Retrieval and evidence ranking
- RAG-based Maintenance Knowledge Assistant
- Maintenance recommendations
- Communication classification and response drafting
- Repair recommendations
- Maintenance scheduling recommendations
- Explainable predictive-risk assessment foundation
- Evidence/source display for AI recommendations
- Human-approval boundary and safe no-autonomous-action design
- Free/local Qwen-based AI runtime foundation
- GitHub Actions CI coverage
- Streamlit AI Intelligence interface

## Phase 4 — Enterprise Integration Foundation 🚧 IN PROGRESS

Phase 4 connects the platform to the enterprise systems used by fleet maintenance operations. The first objective is **integration contracts and canonical envelopes**, not direct production API credentials.

### Phase 4 integration boundaries

- TMT — work orders, maintenance status, completion information
- OEM — fault/campaign/service information
- ELD — vehicle/driver/telemetry events
- PFJ — service/location transaction information
- Vendors — estimates, invoices, repair/service updates
- Notifications — future email/voicemail/operational notifications

### Phase 4 foundation currently implemented

- Common `IntegrationAdapter` contract
- Canonical `IntegrationRecord` envelope
- Source-specific identity and record type
- Equipment-level correlation field
- Event timestamp normalization
- Payload isolation from vendor-specific schemas
- Cursor-aware batch interface
- Duplicate external-record detection
- Integration validation result model
- Synthetic adapters for CI/demo without credentials
- Automated Phase 4 integration contract tests

### Phase 4 next steps

1. Define source-specific mapping contracts for TMT, OEM, ELD, PFJ, and vendors.
2. Add configuration-driven connection profiles without storing secrets in the repository.
3. Build file/API adapters behind the common contract.
4. Add idempotency and replay handling.
5. Add ingestion audit records and integration health metrics.
6. Connect validated integration events to the existing canonical data foundation.
7. Add safe notification adapters with human approval where required.
8. Expose integration health and freshness in Streamlit.

**No live enterprise credentials or production API calls are included in Phase 4 foundation work.**

## Business UI

The Streamlit application provides a single business-facing application with separate areas for:

- **Data Foundation** — fleet, PM, faults, work orders, driver requests, vendors, invoices, compliance, and data quality
- **AI Intelligence** — knowledge assistant, maintenance recommendations, communication assistance, repair recommendations, scheduling, and predictive risk
- **Human Approval** — review items that require human decisions before operational action

Run locally:

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open `http://localhost:8501`.

## Architecture

```text
TMT / OEM / ELD / PFJ / Vendors / Files / Communications
                         │
                         ▼
                Phase 4 Integration Layer
                         │
                 Canonical Envelopes
                         │
                         ▼
              Phase 1 Data Foundation
                         │
                         ▼
              Phase 2 Operational Data
                         │
                         ▼
          Phase 3 Knowledge + RAG + AI
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Recommendations Risk   Scheduling
              │          │          │
              └──────────┼──────────┘
                         ▼
                 Human Approval
                         │
                         ▼
              Safe Operational Action
```

See [HLD.md](HLD.md) for the high-level design and [docs/roadmap.md](docs/roadmap.md) for implementation phases.

## Safety Principle

AI is the intelligence layer, not the authority layer. Safety-critical, compliance-sensitive, financial, and return-to-service decisions remain subject to deterministic policy controls and required human approval.

## Development

The project currently uses Python and synthetic data so the platform can be demonstrated without proprietary TMT, OEM, ELD, or PFJ credentials.

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
pytest -q
```

## Project Status

| Phase | Status | Scope |
|---|---|---|
| Phase 1 | ✅ Complete | Data foundation, quality, validation, curated data, deterministic rules, tests, CI, Streamlit explorer |
| Phase 2 | ✅ Complete | Operational communication/vendor data, reconciliation, review queue, quality tests, Streamlit views |
| Phase 3 | ✅ Complete | Knowledge foundation, RAG, AI recommendations, scheduling, communication, predictive risk, human approval |
| Phase 4 | 🚧 In Progress | Enterprise integration contracts, canonical envelopes, adapters, idempotency, auditability, integration health |
| Phase 5 | ⏳ Planned | Predictive maintenance and telemetry data |
| Phase 6 | ⏳ Planned | Enterprise optimization, feedback, and outcome data |

**Phase 1, Phase 2, and Phase 3 are complete. Phase 4 has started with the enterprise integration foundation.**
