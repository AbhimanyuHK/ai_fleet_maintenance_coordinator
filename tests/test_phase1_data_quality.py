from pathlib import Path

from app.data_quality import phase1_quality_report


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase1"


def test_phase1_quality_report_has_expected_datasets():
    report = phase1_quality_report(DATA)
    datasets = set(report["dataset"])
    assert {
        "equipment_master",
        "pm_schedule",
        "maintenance_history",
        "fault_events",
        "work_orders",
        "vendor_master",
        "service_locations",
        "equipment_availability",
        "campaigns",
        "compliance_inspections",
    }.issubset(datasets)


def test_phase1_quality_report_schema_is_stable():
    report = phase1_quality_report(DATA)
    assert {"dataset", "check", "passed", "failures", "detail"}.issubset(report.columns)
    assert len(report) > 20
