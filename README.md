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

### Phase 1 architecture

```text
TMT / OEM / ELD / PFJ / Vendors / Files
                    │
                    ▼
                   RAW
                    │
                    ▼
                VALIDATED
                    │
                    ▼
              STANDARDIZED
                    │
                    ▼
                CANONICAL
                    │
                    ▼
                 CURATED
                    │
                    ▼
          Deterministic Rules
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
         PM       Fault    Work Orders
        Queue      Queue      Queue
                    │
                    ▼
             Phase 1 Ready
                    │
                    ▼
             Future AI Layer
```

**AI models are intentionally not part of Phase 1.** The objective is to ensure that downstream AI receives governed, traceable, validated data rather than raw source records.

## Phase 1 Business UI

A Streamlit application is available in `streamlit_app.py` for business users to inspect the Phase 1 input data.

It provides:

- Fleet and dataset KPIs
- Interactive dataset explorer
- Search across input data
- Missing-cell and column-quality snapshot
- PM scheduling view
- Critical/high fault view
- Aged work-order view
- Vendor view

Run locally:

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open `http://localhost:8501`.

## MVP / Future AI Scope

Phase 1 is the data foundation. Future phases will build on it to deliver:

- AI-generated daily maintenance priority queue
- Driver email/voicemail classification and response assistance
- Vendor estimate and invoice analysis
- OEM/company knowledge RAG
- Maintenance scheduling optimization
- Predictive maintenance and telemetry analytics
- Human-in-the-loop workflow automation

## Architecture

```text
External Systems
  -> Integration Layer
  -> Event / Data Layer
  -> Fleet Maintenance Domain
  -> Rules + AI/ML + RAG
  -> Workflow Orchestrator
  -> Human Approval / Safe Automation
  -> Dashboard / Notifications / TMT
```

See [HLD.md](HLD.md) for the high-level design and [docs/roadmap.md](docs/roadmap.md) for implementation phases.

## Safety Principle

AI is the intelligence layer, not the authority layer. Safety-critical, compliance-sensitive, financial, and return-to-service decisions remain subject to deterministic policy controls and required human approval.

## Development

The project currently uses Python and synthetic data so the platform can be demonstrated without proprietary TMT, OEM, ELD, or PFJ credentials. Phase 1 has passed automated CI tests.

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
| Phase 2 | ⏳ Planned | Communication/document data foundation and workflow inputs |
| Phase 3 | ⏳ Planned | OEM/company knowledge and RAG data foundation |
| Phase 4 | ⏳ Planned | Scheduling and workflow optimization data |
| Phase 5 | ⏳ Planned | Predictive maintenance and telemetry data |
| Phase 6 | ⏳ Planned | Enterprise optimization, feedback, and outcome data |

**Phase 1 is complete and is the baseline for all subsequent phases.**
