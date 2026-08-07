"""Phase 4 source ingestion, idempotency, audit, and freshness primitives."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from app.integrations import IntegrationAdapter, IntegrationRecord


@dataclass(frozen=True)
class AuditEvent:
    source: str
    action: str
    external_id: str
    occurred_at: datetime
    accepted: bool
    detail: str = ""


@dataclass
class IntegrationStore:
    """In-memory reference store; production persistence is intentionally deferred."""
    records: dict[tuple[str, str, str], IntegrationRecord] = field(default_factory=dict)
    audit: list[AuditEvent] = field(default_factory=list)

    def ingest(self, adapter: IntegrationAdapter, records: Iterable[IntegrationRecord]) -> int:
        accepted = 0
        now = datetime.now(timezone.utc)
        for record in records:
            key = (record.source.value, record.record_type, record.external_id)
            if key in self.records:
                self.audit.append(AuditEvent(record.source.value, "DUPLICATE_SKIPPED", record.external_id, now, False, "idempotency key already exists"))
                continue
            if record.source != adapter.source:
                self.audit.append(AuditEvent(record.source.value, "REJECTED", record.external_id, now, False, "adapter source mismatch"))
                continue
            self.records[key] = record
            self.audit.append(AuditEvent(record.source.value, "INGESTED", record.external_id, now, True))
            accepted += 1
        return accepted

    def latest_event(self, source: str) -> datetime | None:
        events = [e.occurred_at for e in self.audit if e.source == source and e.accepted]
        return max(events) if events else None

    def freshness(self, source: str, now: datetime | None = None) -> str:
        latest = self.latest_event(source)
        if latest is None:
            return "NO_DATA"
        current = now or datetime.now(timezone.utc)
        age_hours = (current - latest).total_seconds() / 3600
        if age_hours < 1:
            return "FRESH"
        if age_hours < 24:
            return "STALE"
        return "OUTDATED"
