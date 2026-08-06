from pathlib import Path
from app.phase2_data_quality import quality_report, reconcile_estimates_invoices, build_review_queue

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase2"


def test_phase2_quality_has_no_error_failures():
    report = quality_report(DATA)
    errors = report[(~report["passed"]) & (report["severity"] == "ERROR")]
    assert errors.empty, errors.to_string(index=False)


def test_invoice_variance_is_detected():
    result = reconcile_estimates_invoices(DATA)
    row = result.loc[result["invoice_id"] == "INV001"].iloc[0]
    assert row["variance"] == 55.0
    assert bool(row["review_required"]) is True


def test_review_queue_contains_safety_and_variance_cases():
    queue = build_review_queue(DATA)
    assert "REQ003" in set(queue.loc[queue["entity_type"] == "driver_request", "entity_id"])
    assert "INV001" in set(queue.loc[queue["entity_type"] == "vendor_invoice", "entity_id"])
    assert "VM003" in set(queue.loc[queue["entity_type"] == "voicemail", "entity_id"])
