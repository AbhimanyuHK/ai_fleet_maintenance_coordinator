from datetime import datetime, timezone

from app.integrations import IntegrationSource, SyntheticAdapter, build_demo_adapters


def test_synthetic_adapter_normalizes_to_canonical_envelope():
    adapter = SyntheticAdapter(
        IntegrationSource.TMT,
        [
            {
                "record_type": "work_order",
                "external_id": "WO-1",
                "equipment_id": "EQ001",
                "occurred_at": "2026-08-07T07:00:00Z",
                "payload": {"status": "OPEN"},
            }
        ],
    )
    batch = adapter.fetch()
    assert len(batch.records) == 1
    record = batch.records[0]
    assert record.source == IntegrationSource.TMT
    assert record.external_id == "WO-1"
    assert record.equipment_id == "EQ001"
    assert record.payload["status"] == "OPEN"
    assert record.occurred_at.tzinfo is not None


def test_adapter_validation_rejects_duplicate_external_records():
    adapter = SyntheticAdapter(IntegrationSource.ELD)
    batch = adapter.fetch()
    batch.records = [
        {
            "source": IntegrationSource.ELD,
            "record_type": "telemetry",
            "external_id": "E-1",
            "occurred_at": datetime.now(timezone.utc),
        }
    ]
    # Rebuild through the model so the validation contract is tested with canonical records.
    from app.integrations import IntegrationBatch, IntegrationRecord

    record = IntegrationRecord(
        source=IntegrationSource.ELD,
        record_type="telemetry",
        external_id="E-1",
        occurred_at=datetime.now(timezone.utc),
    )
    validated = adapter.validate(IntegrationBatch(source=IntegrationSource.ELD, records=[record, record], fetched_at=datetime.now(timezone.utc)))
    assert validated.accepted == 1
    assert validated.rejected == 1
    assert "duplicate external record" in validated.errors[0]


def test_demo_boundaries_cover_required_phase4_sources():
    adapters = build_demo_adapters()
    required = {IntegrationSource.TMT, IntegrationSource.OEM, IntegrationSource.ELD, IntegrationSource.PFJ, IntegrationSource.VENDOR}
    assert required.issubset(adapters)
    for source in required:
        result = adapters[source].validate(adapters[source].fetch())
        assert result.accepted == 1
        assert result.rejected == 0
        assert not result.errors
