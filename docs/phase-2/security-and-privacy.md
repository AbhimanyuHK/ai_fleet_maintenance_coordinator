# Phase 2 Security and Privacy Controls

Phase 2 introduces communications, audio, documents, and potentially personally identifiable information. Data preparation must therefore include security controls before AI processing.

## Principles

- Minimize PII.
- Separate identity metadata from operational text where practical.
- Hash email addresses and phone numbers in analytical datasets.
- Store source documents/audio in controlled object storage.
- Never expose raw artifact URLs in business-facing tables.
- Preserve content hashes and source lineage.
- Encrypt data in transit and at rest in production.
- Apply retention policies by artifact type.
- Restrict human review access by role.
- Record reviewer actions in an audit trail.

## AI boundary

Raw documents and audio should pass through security, malware/content checks, type validation, and data-quality controls before any future model invocation.

```text
Raw artifact
   ↓
Security/type checks
   ↓
PII minimization
   ↓
Validated text/metadata
   ↓
AI processing (future)
   ↓
Evidence + model output
   ↓
Human review
   ↓
Controlled workflow action
```

## Safety boundary

A classification such as safety-critical or compliance-critical is an operational signal, not authorization to repair, dispatch, or return equipment to service. Deterministic policy and human approval remain required.
