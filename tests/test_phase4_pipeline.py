from datetime import datetime, timedelta, timezone

from app.integration_pipeline import IntegrationStore
from app.integrations import IntegrationSource, SyntheticAdapter


def record():
    return {
        "record_type": "work_order",
        "external_id": "WO-100",
        "equipment_id": "EQ001",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "payload": {"status": "OPEN"},
    }


def test_ingestion_is_idempotent():
    adapter = SyntheticAdapter(IntegrationSource.TMT, [record()])
    batch = adapter.fetch()
    store = IntegrationStore()
    assert store.ingest(adapter, batch.records) == 1
    assert store.ingest(adapter, batch.records) == 0
    assert len(store.records) == 1
    assert store.audit[-1].action == "DUPLICATE_SKIPPED"


def test_freshness_states():
    adapter = SyntheticAdapter(IntegrationSource.OEM, [record()])
    store = IntegrationStore()
    store.ingest(adapter, adapter.fetch().records)
    latest = store.latest_event("OEM")
    assert latest is not None
    assert store.freshness("OEM", latest + timedelta(minutes=30)) == "FRESH"
    assert store.freshness("OEM", latest + timedelta(hours=2)) == "STALE"
    assert store.freshness("OEM", latest + timedelta(hours=25)) == "OUTDATED"
    assert store.freshness("ELD") == "NO_DATA"
