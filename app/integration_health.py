"""Business-facing integration health reporting."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from app.integration_pipeline import IntegrationStore
from app.integrations import IntegrationSource


@dataclass(frozen=True)
class SourceHealth:
    source: str
    freshness: str
    accepted: int
    rejected: int
    duplicates: int
    last_ingestion: datetime | None


def build_health_report(store: IntegrationStore) -> list[SourceHealth]:
    result: list[SourceHealth] = []
    for source in IntegrationSource:
        events = [event for event in store.audit if event.source == source.value]
        accepted = sum(event.accepted and event.action == "INGESTED" for event in events)
        rejected = sum(not event.accepted and event.action == "REJECTED" for event in events)
        duplicates = sum(event.action == "DUPLICATE_SKIPPED" for event in events)
        result.append(SourceHealth(source.value, store.freshness(source.value), accepted, rejected, duplicates, store.latest_event(source.value)))
    return result
