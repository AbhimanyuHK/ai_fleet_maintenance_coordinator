# Phase 2 Data Requirements — AI Intake Foundation

## Objective

Prepare trustworthy, traceable data for the maintenance communication and document-intake workflows described in Phase 2. AI models are not required to complete the data foundation.

Phase 2 must support:

1. Driver email classification
2. Voicemail transcription intake
3. Vendor estimate extraction
4. Vendor invoice extraction
5. Repair-note summarization
6. Human review and approval

## Core principle

```text
Email / Voicemail / Estimate / Invoice / Repair Note
                         ↓
                       RAW
                         ↓
                VALIDATED + SECURED
                         ↓
                 STANDARDIZED TEXT
                         ↓
              CANONICAL INTAKE RECORD
                         ↓
                HUMAN REVIEW QUEUE
                         ↓
                 Future AI Services
```

Do not send untrusted raw documents directly to an AI model.

## Canonical Phase 2 datasets

| Dataset | Grain | Primary key | Purpose |
|---|---|---|---|
| communication_messages | one inbound/outbound communication | message_id | Email/SMS/other message metadata and body references |
| voicemail_records | one voicemail | voicemail_id | Audio metadata and transcription lifecycle |
| driver_requests | one maintenance request | request_id | Normalized driver maintenance concern |
| vendor_estimates | one vendor estimate | estimate_id | Estimate header, amounts, work-order linkage |
| vendor_estimate_lines | one estimate line | estimate_line_id | Parts/labor/SRT detail |
| vendor_invoices | one vendor invoice | invoice_id | Final billing and reconciliation |
| vendor_invoice_lines | one invoice line | invoice_line_id | Parts/labor/tax/detail |
| repair_notes | one repair note/event | repair_note_id | Diagnosis, correction, technician notes |
| document_artifacts | one source artifact | artifact_id | Secure document/audio/text lineage |
| human_review_tasks | one review task | review_task_id | Human-in-the-loop decision and audit trail |
| communication_participants | one message participant | participant_id | Sender/recipient/driver/vendor identity |

## Required fields

### communication_messages

`message_id`, `channel`, `direction`, `received_at`, `sender_ref`, `recipient_ref`, `subject`, `body_text`, `artifact_id`, `equipment_id`, `request_id`, `source_system`, `source_record_id`, `ingested_at`.

### voicemail_records

`voicemail_id`, `received_at`, `caller_ref`, `phone_hash`, `audio_artifact_id`, `duration_seconds`, `equipment_id`, `request_id`, `transcription_status`, `source_system`, `source_record_id`, `ingested_at`.

### driver_requests

`request_id`, `equipment_id`, `driver_ref`, `created_at`, `channel`, `request_text`, `safety_related`, `compliance_related`, `urgency`, `status`, `work_order_id`, `source_message_id`, `source_voicemail_id`.

### vendor_estimates

`estimate_id`, `vendor_id`, `equipment_id`, `work_order_id`, `estimate_number`, `received_at`, `currency`, `subtotal`, `tax`, `total`, `labor_total`, `parts_total`, `warranty_claimed`, `artifact_id`, `source_system`, `source_record_id`, `ingested_at`.

### vendor_estimate_lines

`estimate_line_id`, `estimate_id`, `line_type`, `description`, `part_number`, `quantity`, `unit_price`, `labor_hours`, `labor_rate`, `srt_code`, `line_total`, `warranty_flag`.

### vendor_invoices

`invoice_id`, `vendor_id`, `equipment_id`, `work_order_id`, `invoice_number`, `invoice_date`, `received_at`, `currency`, `subtotal`, `tax`, `total`, `labor_total`, `parts_total`, `warranty_credit`, `artifact_id`, `source_system`, `source_record_id`, `ingested_at`.

### vendor_invoice_lines

`invoice_line_id`, `invoice_id`, `line_type`, `description`, `part_number`, `quantity`, `unit_price`, `labor_hours`, `labor_rate`, `srt_code`, `line_total`, `warranty_flag`.

### repair_notes

`repair_note_id`, `work_order_id`, `equipment_id`, `vendor_id`, `created_at`, `technician_ref`, `complaint`, `diagnosis`, `correction`, `parts_used`, `labor_hours`, `return_to_service`, `artifact_id`, `source_system`, `source_record_id`, `ingested_at`.

### document_artifacts

`artifact_id`, `artifact_type`, `mime_type`, `storage_uri`, `content_hash`, `size_bytes`, `created_at`, `received_at`, `retention_class`, `classification`, `source_system`, `source_record_id`, `ingested_at`.

Never store sensitive raw audio/document content in ordinary analytical tables. Store a controlled reference plus hash and metadata.

### human_review_tasks

`review_task_id`, `task_type`, `entity_type`, `entity_id`, `priority`, `reason`, `assigned_to`, `created_at`, `due_at`, `status`, `decision`, `decision_reason`, `reviewed_at`, `reviewer_ref`.

### communication_participants

`participant_id`, `message_id`, `participant_role`, `party_type`, `party_ref`, `display_name`, `email_hash`, `phone_hash`.

## Relationships

```text
equipment_master
    ├── driver_requests
    ├── communication_messages
    ├── voicemail_records
    ├── vendor_estimates
    ├── vendor_invoices
    └── repair_notes

work_orders
    ├── driver_requests
    ├── vendor_estimates
    ├── vendor_invoices
    └── repair_notes

vendor_master
    ├── vendor_estimates
    ├── vendor_invoices
    └── repair_notes

vendor_estimates
    └── vendor_estimate_lines

vendor_invoices
    └── vendor_invoice_lines

communication_messages
    ├── communication_participants
    └── driver_requests

all source artifacts
    └── document_artifacts

all AI-assisted decisions
    └── human_review_tasks
```

## Data-quality rules

1. Every artifact has a stable content hash for duplicate detection.
2. Every inbound record has source and ingestion lineage.
3. Equipment/work-order/vendor references must resolve when supplied.
4. Estimate and invoice totals must reconcile with their line items within configured rounding tolerance.
5. Quantities, rates, hours, and monetary values cannot be negative.
6. Invoice date cannot precede estimate/repair context without an explicit exception.
7. Transcription status must distinguish unavailable, pending, successful, and failed.
8. Safety/compliance indicators must never default to false when evidence is unavailable.
9. Review tasks must preserve original evidence references and reviewer decisions.
10. PII should be minimized, hashed/tokenized where appropriate, and never copied unnecessarily into model prompts.
11. Duplicate messages, audio, estimates, and invoices must be detectable by source identity and content hash.
12. Failed parsing/extraction must be retained as a traceable error state rather than silently discarded.

## Phase 2 acceptance criteria

- All 11 canonical datasets have schemas and data dictionaries.
- Synthetic data covers normal and adverse document/intake cases.
- Email, voicemail, estimate, invoice, and repair-note records can be linked to equipment/work orders.
- Document lineage and content hashes are available.
- Financial totals reconcile deterministically.
- PII/security controls are documented.
- Human review tasks can capture approval/rejection and evidence.
- Data-quality reports run automatically in CI.
- No AI model is required for the Phase 2 data-foundation gate.
