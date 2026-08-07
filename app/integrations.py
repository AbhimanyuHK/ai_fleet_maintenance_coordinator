"""Phase 4 enterprise integration contracts and safe synthetic adapters.

This module deliberately contains no live credentials or vendor-specific API calls.
It defines the boundary between external systems and the canonical fleet domain so
real connectors can be added without coupling business rules to a vendor API.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable

from pydantic import BaseModel, Field


class IntegrationSource(str, Enum):
    TMT = "TMT"
    OEM = "OEM"
    ELD = "ELD"
    PFJ = "PFJ"
    VENDOR = "VENDOR"
    NOTIFICATION = "NOTIFICATION"


class IntegrationRecord(BaseModel):
    """Canonical envelope for an external-system event or record."""

    source: IntegrationSource
    record_type: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    occurred_at: datetime
    equipment_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class IntegrationBatch(BaseModel):
    source: IntegrationSource
    records: list[IntegrationRecord] = Field(default_factory=list)
    fetched_at: datetime
    cursor: str | None = None


class IntegrationResult(BaseModel):
    source: IntegrationSource
    accepted: int = 0
    rejected: int = 0
    errors: list[str] = Field(default_factory=list)


class IntegrationAdapter(ABC):
    """Adapter contract used by all Phase 4 external integrations."""

    source: IntegrationSource

    @abstractmethod
    def fetch(self, cursor: str | None = None) -> IntegrationBatch:
        """Fetch source records without exposing vendor-specific payloads downstream."""

    def normalize(self, records: Iterable[dict[str, Any]]) -> list[IntegrationRecord]:
        normalized: list[IntegrationRecord] = []
        for record in records:
            normalized.append(
                IntegrationRecord(
                    source=self.source,
                    record_type=str(record["record_type"]),
                    external_id=str(record["external_id"]),
                    occurred_at=_parse_datetime(record["occurred_at"]),
                    equipment_id=_optional_string(record.get("equipment_id")),
                    payload=dict(record.get("payload", {})),
                )
            )
        return normalized

    def validate(self, batch: IntegrationBatch) -> IntegrationResult:
        accepted = 0
        rejected = 0
        errors: list[str] = []
        seen: set[tuple[str, str]] = set()
        for record in batch.records:
            key = (record.record_type, record.external_id)
            if key in seen:
                rejected += 1
                errors.append(f"duplicate external record: {record.record_type}/{record.external_id}")
                continue
            seen.add(key)
            if record.source != self.source:
                rejected += 1
                errors.append(f"source mismatch: expected {self.source}, got {record.source}")
                continue
            accepted += 1
        return IntegrationResult(source=self.source, accepted=accepted, rejected=rejected, errors=errors)


class SyntheticAdapter(IntegrationAdapter):
    """Deterministic adapter for CI, demos, and Streamlit without live credentials."""

    def __init__(self, source: IntegrationSource, records: list[dict[str, Any]] | None = None):
        self.source = source
        self._records = records or []

    def fetch(self, cursor: str | None = None) -> IntegrationBatch:
        start = int(cursor or 0)
        selected = self._records[start:]
        normalized = self.normalize(selected)
        next_cursor = str(start + len(selected)) if selected else None
        return IntegrationBatch(
            source=self.source,
            records=normalized,
            fetched_at=datetime.now(timezone.utc),
            cursor=next_cursor,
        )


def build_demo_adapters() -> dict[IntegrationSource, SyntheticAdapter]:
    """Return safe adapters representing the Phase 4 integration boundaries."""

    now = datetime.now(timezone.utc).isoformat()
    demo = {
        IntegrationSource.TMT: [{"record_type": "work_order", "external_id": "TMT-WO-001", "equipment_id": "EQ001", "occurred_at": now, "payload": {"status": "OPEN"}}],
        IntegrationSource.OEM: [{"record_type": "fault_event", "external_id": "OEM-F-001", "equipment_id": "EQ001", "occurred_at": now, "payload": {"fault_code": "BRAKE"}}],
        IntegrationSource.ELD: [{"record_type": "telemetry_event", "external_id": "ELD-E-001", "equipment_id": "EQ001", "occurred_at": now, "payload": {"engine_hours": 1250}}],
        IntegrationSource.PFJ: [{"record_type": "service_transaction", "external_id": "PFJ-S-001", "equipment_id": "EQ001", "occurred_at": now, "payload": {"location": "PFJ-001"}}],
        IntegrationSource.VENDOR: [{"record_type": "invoice", "external_id": "V-INV-001", "equipment_id": "EQ001", "occurred_at": now, "payload": {"total": 850.0}}],
    }
    return {source: SyntheticAdapter(source, records) for source, records in demo.items()}


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _optional_string(value: Any) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    return str(value)
