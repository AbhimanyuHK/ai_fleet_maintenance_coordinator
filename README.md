# AI Fleet Maintenance Coordinator

AI-powered Fleet Maintenance Operations Automation Platform.

## Vision

Reduce preventable breakdowns, improve fleet uptime and safety, reduce maintenance cost leakage, recover warranty value, and reduce manual coordination work.

## What is the AI Fleet Maintenance Coordinator?

The AI Fleet Maintenance Coordinator is a **decision-support layer for fleet maintenance operations**. It brings maintenance information together, checks whether the data is trustworthy and current, identifies what needs attention, retrieves approved maintenance knowledge, and prepares recommendations for the maintenance team.

It is **not an autonomous authority**. Safety-critical, compliance-sensitive, financial, return-to-service, and other consequential decisions remain subject to deterministic controls and required human approval.

The intended business flow is:

```text
Fleet / Enterprise Sources
        ↓
Trusted Data Foundation
        ↓
Integration Health + Freshness Gate
        ↓
Knowledge + RAG + AI Reasoning
        ↓
Recommendations / Risk / Scheduling / Communication
        ↓
Human Review & Approval
        ↓
Safe Operational Action
        ↓
Outcome / Feedback
```

The Streamlit application includes a **📘 Fleet Maintenance AI Coordinator — Business Guide** page that explains the operating model, business problems, PM scheduling use case, AI capabilities, business impact, maintenance economics, human-approval boundary, and recommended rollout.

## Business Impact & Value Proposition

The business objective is not simply to add an AI chatbot. The objective is to help a maintenance organization move from **reactive coordination and information chasing** toward **proactive, evidence-based maintenance decisions**.

### Why the tool is required

Fleet maintenance information is usually distributed across fleet systems, OEM sources, ELD/telematics, vendors, driver communications, work orders, PM schedules, invoices, and maintenance documents. A coordinator may need to manually connect these signals before deciding what should happen next.

The coordinator addresses recurring operational problems:

- PM work is missed, delayed, or manually chased.
- Faults compete for attention and may not be triaged consistently.
- Safety-related driver requests can be buried among routine requests.
- Coordinators and technicians spend time searching maintenance history and approved knowledge.
- Vehicle downtime can increase when repair, service-location, parts, and availability information are fragmented.
- Vendor estimates and invoices can contain variances that require manual comparison.
- Driver and vendor communication consumes coordinator time.
- Management may lack one current view of PM compliance, faults, backlog, downtime, data quality, and risk.

### How AI improves the business

| Business area | AI Coordinator assistance | Expected business outcome |
|---|---|---|
| PM management | Prioritize due, overdue, and at-risk maintenance | Better PM discipline and fewer avoidable failures |
| Fault triage | Combine severity, history, equipment context, and safety signals | Faster response and better maintenance prioritization |
| Downtime | Help coordinate repair priority, service location, and availability | Improve fleet availability and reduce avoidable downtime |
| Maintenance knowledge | Retrieve approved knowledge and summarize relevant evidence | Less searching and faster decision preparation |
| Repair support | Use history and approved knowledge to prepare repair options | More consistent repair decisions |
| Scheduling | Recommend maintenance timing using operational context | Better maintenance capacity and vehicle utilization |
| Driver communication | Classify requests and draft context-aware responses | Faster communication with human review |
| Vendor control | Highlight estimate/invoice differences for review | Better cost control and reduced leakage |
| Risk | Explain which equipment/events deserve attention | Earlier intervention and better risk visibility |
| Management | Provide one operational picture | Better planning and accountability |

### Maintenance cost: manual vs AI-assisted coordination

The business case should compare the current manual operating model with an AI-assisted model using **actual fleet data**, not an assumed AI savings percentage.

Important cost/value components include:

1. **Coordinator labor** — time spent searching systems, chasing PMs, preparing reports, copying information, and following up with drivers/vendors.
2. **Breakdown and reactive-repair cost** — parts, labor, towing, emergency service, and other costs associated with preventable or poorly anticipated failures.
3. **Vehicle downtime** — lost productive utilization while equipment is unavailable for service.
4. **PM effectiveness** — the financial difference between planned maintenance and avoidable reactive maintenance.
5. **Vendor leakage** — estimate/invoice variances, duplicate charges, unexpected scope, and missed warranty/recovery opportunities.
6. **Communication workload** — time spent reading, classifying, routing, and responding to maintenance requests.
7. **AI/platform cost** — model runtime, hosting, integration, observability, support, and implementation costs.

A simple business-case model is:

```text
Annual AI-Assisted Value
    = Coordinator Time Recovered
    + Avoidable Downtime Value Recovered
    + Maintenance Cost Avoidance
    + Vendor Leakage Avoided
    + Other Measured Operational Benefits

Net Annual Value
    = Annual AI-Assisted Value - Annual AI/Platform Cost

ROI %
    = Net Annual Value / Annual AI/Platform Cost × 100
```

The Streamlit **📘 Business Guide** includes an illustrative calculator for coordinator-time recovery and downtime value. It is intentionally labeled as a planning tool, not a financial forecast. Before a purchase or production rollout, replace the assumptions with finance-approved baseline data.

### What should be measured in a pilot

A practical baseline should include:

- PM compliance rate
- Preventive vs reactive maintenance ratio
- Breakdown frequency
- Average vehicle downtime per event
- Maintenance cost per vehicle / mile / operating hour, as appropriate
- Coordinator hours spent on repetitive work
- Average response time to driver maintenance requests
- Vendor estimate-to-invoice variance
- Work-order aging
- Vehicle availability/utilization
- Safety/compliance escalations
- AI recommendation acceptance/rejection rate
- AI-assisted time saved

This allows the business to prove value from measured outcomes rather than claiming that AI automatically reduces costs.

### AI Coordinator vs manual coordination

| Activity | Mostly manual coordination | AI Coordinator assistance |
|---|---|---|
| PM follow-up | Review schedules and chase tasks | Prioritize due/at-risk PM work |
| Fault investigation | Search several systems | Combine context and summarize evidence |
| Repair decision support | Search history/manuals | Retrieve approved knowledge and prepare options |
| Scheduling | Coordinate availability manually | Suggest priority/time/location based on constraints |
| Driver communication | Read, classify, draft, route | Classify and draft with human approval |
| Vendor review | Compare documents manually | Highlight estimate/invoice variances |
| Risk review | Spreadsheet/report driven | Explainable risk prioritization |
| Management reporting | Manual aggregation | Unified operational view |

The target is **human + AI**, not simply human replacement. The AI handles repetitive analysis and preparation so maintenance professionals can spend more time on exceptions, safety, vendor decisions, field coordination, and operational judgment.

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

Phase 4 connects the platform to the enterprise systems used by fleet maintenance operations. The first objective is **integration contracts, canonical envelopes, data freshness, and safe orchestration**, not direct production API credentials.

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
- Configuration-driven source profiles
- Authentication-mode boundary without repository secrets
- Retry and transient-error orchestration
- Source freshness SLA scheduling
- Integration health and audit foundations
- AI freshness gate
- Workflow-specific AI readiness policy
- Streamlit AI Data Readiness experience
- Business-facing coordinator guidance page with business impact and cost framework

### Phase 4 remaining steps

1. Harden source-specific mapping contracts for TMT, OEM, ELD, PFJ, and vendors.
2. Build file/API adapters behind the common contract.
3. Add production secret references and deployment configuration without storing secrets in the repository.
4. Add durable scheduling and replay handling for real ingestion jobs.
5. Connect validated integration events to the canonical data foundation in production environments.
6. Add safe notification adapters with human approval where required.
7. Validate integration health, freshness, and AI readiness against real enterprise SLAs.

**No live enterprise credentials or production API calls are included in the Phase 4 foundation work.**

## Business UI

The Streamlit application provides a business-facing experience with:

- **📘 Coordinator Guide** — explains the fleet maintenance coordinator, business problems, PM scheduling, AI capabilities, business impact, manual-vs-AI-assisted cost framework, human approval, KPIs, and rollout approach
- **📊 Data Foundation** — fleet, PM, faults, work orders, driver requests, vendors, invoices, compliance, and data quality
- **🤖 AI Intelligence** — knowledge assistant, maintenance recommendations, communication assistance, repair recommendations, scheduling, predictive risk, and AI data readiness
- **👤 Human Approval** — review items that require human decisions before operational action

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
            Canonical Envelopes + Health
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
                  Freshness Gate
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
                         │
                         ▼
                   Outcomes / Feedback
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
| Phase 4 | 🚧 In Progress | Enterprise integration contracts, configuration, orchestration, freshness/SLA, health, AI readiness, business guidance |
| Phase 5 | ⏳ Planned | Predictive maintenance and telemetry data |
| Phase 6 | ⏳ Planned | Enterprise optimization, feedback, and outcome data |

**Phase 1, Phase 2, and Phase 3 are complete. Phase 4 is progressing through the enterprise integration foundation and AI-readiness boundary.**
