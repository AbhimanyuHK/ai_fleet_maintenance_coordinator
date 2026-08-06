# High-Level Design — AI Fleet Maintenance Coordinator

## 1. Objective

Build an AI-powered fleet maintenance platform that monitors preventive maintenance, equipment health, repair activity, vendor estimates/invoices, warranty opportunities, driver requests, work-order aging, and compliance signals.

The platform reduces repetitive coordination while keeping safety, FMCSA compliance, financial approvals, company policy, and required human decisions protected.

## 2. Business Outcomes

1. Reduce preventable roadside breakdowns.
2. Improve fleet uptime and PM compliance.
3. Detect safety-critical issues faster.
4. Reduce invoice and repair cost leakage.
5. Increase warranty recovery.
6. Reduce manual maintenance coordination.
7. Improve vendor performance visibility.
8. Provide a daily maintenance control tower for management.

## 3. Architecture

```text
PM / OEM / ELD / PFJ / TMT / Vendor / Email / Voicemail
                         |
                         v
                 Integration Layer
                         |
                         v
                Event + Data Layer
                         |
             +-----------+-----------+
             |                       |
             v                       v
       Operational DB           Data Lake / DW
             |                       |
             +-----------+-----------+
                         |
                         v
                AI / ML / RAG Layer
                         |
               Rules + Policy Engine
                         |
                         v
                 Workflow Engine
                         |
             +-----------+-----------+
             |                       |
             v                       v
      Safe Automation         Human Approval
             |                       |
             +-----------+-----------+
                         |
                         v
                Dashboard / TMT /
                 Notifications
```

## 4. Core Components

### Integration Layer

Adapters for TMT, OEM dashboards, ELD, PFJ, vendors, email, voicemail, files, and future APIs. Where APIs are unavailable, controlled file ingestion or RPA may be considered.

### Fleet Maintenance Domain

Canonical entities include equipment, PM schedules, faults, work orders, vendors, estimates, invoices, warranty events, campaigns, compliance events, and communications.

### Rules Engine

Deterministic rules handle PM deadlines, safety escalation, approval thresholds, work-order SLA, and compliance requirements.

### AI Layer

LLMs handle unstructured text and documents: driver communication classification, estimate/invoice extraction, repair-note summarization, grounded maintenance assistance, and communication drafting.

### ML Layer

Future models can predict failure risk, breakdown probability, repair duration, PM demand, vendor performance, and parts demand.

### RAG

Ground AI recommendations in approved OEM manuals, service bulletins, campaigns, recalls, company policies, FMCSA material, vendor agreements, SRT/VMRS references, warranty policies, and internal procedures.

### Workflow Engine

Coordinates detection, enrichment, risk scoring, scheduling recommendations, approvals, escalations, notifications, and downstream updates.

## 5. First Automation — PM Monitoring

Every day:

```text
Load PM data
 -> calculate days/miles remaining
 -> check scheduling status
 -> check equipment availability
 -> identify preferred vendor/location
 -> assess operational disruption
 -> recommend service date
 -> create alert/approval task
```

The business rule is explicit: PM service should be proactively scheduled at least five days before the due date.

## 6. Fault Prioritization

```text
Fault event
 -> normalize code
 -> enrich with equipment history
 -> apply deterministic severity rules
 -> calculate risk score
 -> AI explanation / recommendation
 -> maintenance queue
```

Critical safety issues are escalated immediately and cannot be downgraded by an LLM.

## 7. Driver Communication

```text
Email / voicemail
 -> transcription / parsing
 -> equipment extraction
 -> issue extraction
 -> safety/compliance classification
 -> priority
 -> task / escalation
```

Examples: brake pressure loss is safety-critical; a cabin-light issue is normally non-urgent. Actual classification must be validated against company policy.

## 8. Vendor Estimate and Invoice Intelligence

Extract labor hours, labor rates, SRT, parts, prices, warranty indicators, taxes, totals, and repair descriptions. Compare estimates and invoices against approved work, national account agreements, SRTs, labor rates, and warranty rules.

Potential discrepancies create review tasks instead of silently approving changes.

## 9. Work-Order Aging

Open work orders are continuously monitored. Work orders older than 30 days require a delay explanation and escalation according to policy.

## 10. Human-in-the-Loop

AI may automatically classify, extract, summarize, detect anomalies, create drafts, and recommend actions. Human approval remains required for safety-critical decisions, financial approvals above thresholds, disputed invoices, warranty decisions, unauthorized repairs, and other policy-defined actions.

## 11. Auditability

Record event time, equipment, source, model/workflow version, retrieved evidence, recommendation, confidence, rule evaluation, human decision, and final action for material AI-assisted decisions.

## 12. Target KPIs

- PMs scheduled >= 5 days ahead
- PM compliance rate
- Roadside breakdown rate
- Fleet uptime
- Safety response time
- Average repair duration
- Work orders >30 days
- Invoice discrepancy rate
- Warranty recovery
- Vendor SLA compliance
- Human override rate
- AI classification/extraction accuracy

## 13. AWS Direction

A future production deployment can use API Gateway, Lambda, EventBridge, SQS, Step Functions, S3, Aurora PostgreSQL, Glue, Redshift/Snowflake, OpenSearch/vector search, CloudWatch, Secrets Manager, IAM, and an AI gateway. Services should be selected based on existing enterprise standards and actual integration capabilities.

## 14. Evolution

```text
Observe -> Detect -> Recommend -> Human Approve -> Automate Low Risk -> Predict -> Semi-autonomous
```

AI should be the intelligence layer, not the authority layer.