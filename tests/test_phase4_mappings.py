import pytest

from app.integration_mappings import (
    SOURCE_MAPPERS,
    map_eld_telemetry,
    map_oem_fault,
    map_pfj_service,
    map_tmt_work_order,
    map_vendor_invoice,
)
from app.integrations import IntegrationSource


def base(**overrides):
    value = {"occurred_at": "2026-08-07T07:00:00Z", "equipment_id": "EQ001", "payload": {"status": "OPEN"}}
    value.update(overrides)
    return value


@pytest.mark.parametrize(
    "mapper, source, record_type, id_field, external_id",
    [
        (map_tmt_work_order, IntegrationSource.TMT, "work_order", "work_order_id", "WO-1"),
        (map_oem_fault, IntegrationSource.OEM, "fault_event", "fault_event_id", "F-1"),
        (map_eld_telemetry, IntegrationSource.ELD, "telemetry_event", "telemetry_event_id", "TEL-1"),
        (map_pfj_service, IntegrationSource.PFJ, "service_transaction", "transaction_id", "TX-1"),
        (map_vendor_invoice, IntegrationSource.VENDOR, "invoice", "invoice_id", "INV-1"),
    ],
)
def test_source_mapping_produces_canonical_result(mapper, source, record_type, id_field, external_id):
    result = mapper(base(**{id_field: external_id}))
    assert result.source == source
    assert result.record_type == record_type
    assert result.external_id == external_id
    assert result.equipment_id == "EQ001"


def test_mapping_requires_external_id():
    with pytest.raises(ValueError, match="required field missing"):
        map_tmt_work_order(base())


def test_mapping_registry_covers_all_phase4_sources():
    expected = {
        (IntegrationSource.TMT, "work_order"),
        (IntegrationSource.OEM, "fault_event"),
        (IntegrationSource.ELD, "telemetry_event"),
        (IntegrationSource.PFJ, "service_transaction"),
        (IntegrationSource.VENDOR, "invoice"),
    }
    assert expected == set(SOURCE_MAPPERS)
