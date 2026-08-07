"""Phase 4 mappings from external source records into canonical fleet events."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.integrations import IntegrationSource


@dataclass(frozen=True)
class MappingResult:
    source: IntegrationSource
    record_type: str
    external_id: str
    equipment_id: str | None
    occurred_at: Any
    payload: dict[str, Any]


def _require(record: dict[str, Any], key: str) -> Any:
    value = record.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"required field missing: {key}")
    return value


def _map(source: IntegrationSource, record: dict[str, Any], record_type: str, id_field: str, equipment_field: str = "equipment_id") -> MappingResult:
    return MappingResult(
        source=source,
        record_type=record_type,
        external_id=str(_require(record, id_field)),
        equipment_id=str(record[equipment_field]) if record.get(equipment_field) not in (None, "") else None,
        occurred_at=_require(record, "occurred_at"),
        payload=dict(record.get("payload", {})),
    )


def map_tmt_work_order(record: dict[str, Any]) -> MappingResult:
    return _map(IntegrationSource.TMT, record, "work_order", "work_order_id")


def map_oem_fault(record: dict[str, Any]) -> MappingResult:
    return _map(IntegrationSource.OEM, record, "fault_event", "fault_event_id")


def map_eld_telemetry(record: dict[str, Any]) -> MappingResult:
    return _map(IntegrationSource.ELD, record, "telemetry_event", "telemetry_event_id")


def map_pfj_service(record: dict[str, Any]) -> MappingResult:
    return _map(IntegrationSource.PFJ, record, "service_transaction", "transaction_id")


def map_vendor_invoice(record: dict[str, Any]) -> MappingResult:
    return _map(IntegrationSource.VENDOR, record, "invoice", "invoice_id")


SOURCE_MAPPERS = {
    (IntegrationSource.TMT, "work_order"): map_tmt_work_order,
    (IntegrationSource.OEM, "fault_event"): map_oem_fault,
    (IntegrationSource.ELD, "telemetry_event"): map_eld_telemetry,
    (IntegrationSource.PFJ, "service_transaction"): map_pfj_service,
    (IntegrationSource.VENDOR, "invoice"): map_vendor_invoice,
}
