# Phase 2 Data Dictionary

## Common lineage fields

| Field | Type | Required | Purpose |
|---|---|---:|---|
| source_system | string | yes | Source application/channel |
| source_record_id | string | yes | Stable source identifier |
| ingested_at | datetime | yes | Platform ingestion time |
| source_updated_at | datetime | no | Source update time |

## Communication

`communication_messages` stores message metadata and normalized text. `communication_participants` separates party identity from message content so PII can be governed independently.

Key enums:

- channel: email, sms, portal, other
- direction: inbound, outbound
- participant_role: sender, recipient, cc, bcc
- party_type: driver, vendor, fleet_team, system, other

## Voice

`voicemail_records` contains metadata and lifecycle state; audio is referenced through `document_artifacts`.

`transcription_status` values: unavailable, pending, successful, failed, reviewed.

## Driver request

A request is the business-level maintenance concern derived from one or more communications. It can exist before a work order and should preserve its source evidence.

Recommended urgency values: emergency, critical, high, normal, low, unknown.

## Estimates and invoices

Financial data is split into headers and lines. This enables deterministic reconciliation and later AI extraction evaluation.

`line_type` values should include labor, part, fee, tax, core, other.

Money must include currency and use decimal arithmetic in production.

## Repair notes

Repair notes retain structured diagnosis/correction information and source evidence. AI summaries, when introduced later, must be separate derived fields and must not overwrite source notes.

## Document artifacts

Artifacts are immutable references to source files/audio/text. `content_hash` supports deduplication. `storage_uri` should point to controlled storage, not expose public documents.

Recommended artifact types: email_attachment, voicemail_audio, estimate_pdf, estimate_image, invoice_pdf, invoice_image, repair_note, other.

## Human review

`human_review_tasks` is the control boundary between AI suggestions and operational action. A review task must retain:

- source entity
- evidence/artifact references
- priority/reason
- reviewer identity
- decision
- decision reason
- timestamps

AI-generated fields should be versioned and traceable rather than replacing source values.
