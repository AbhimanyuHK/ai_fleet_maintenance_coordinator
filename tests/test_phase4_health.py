from datetime import datetime, timezone
from app.integration_health import build_health_report
from app.integration_pipeline import IntegrationStore
from app.integrations import IntegrationSource, SyntheticAdapter


def test_health_report_includes_all_sources_and_counts():
    store = IntegrationStore()
    adapter = SyntheticAdapter(IntegrationSource.TMT, [{"record_type":"work_order","external_id":"WO-1","equipment_id":"EQ001","occurred_at":datetime.now(timezone.utc).isoformat(),"payload":{}}])
    records = adapter.fetch().records
    store.ingest(adapter, records)
    store.ingest(adapter, records)
    report = {item.source: item for item in build_health_report(store)}
    assert set(report) == {source.value for source in IntegrationSource}
    assert report["TMT"].accepted == 1
    assert report["TMT"].duplicates == 1
    assert report["TMT"].freshness == "FRESH"
    assert report["OEM"].freshness == "NO_DATA"
