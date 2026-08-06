from pathlib import Path
from app.communication_assistant import assess
from app.phase3_retrieval import load_chunks

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = load_chunks(ROOT / "data" / "phase3" / "knowledge")


def test_driver_brake_report_is_critical():
    result = assess("EQ001 brake pedal feels abnormal and vehicle cannot stop safely", CHUNKS, "EQ001")
    assert result.safety_related is True
    assert result.priority == "CRITICAL"
    assert result.category == "SAFETY"
    assert result.human_approval_required is True


def test_compliance_request_is_high():
    result = assess("The ELD inspection documentation is missing for EQ002", CHUNKS, "EQ002")
    assert result.compliance_related is True
    assert result.priority == "HIGH"
    assert result.category == "COMPLIANCE"


def test_normal_request_is_medium():
    result = assess("Please arrange service for the cabin light on EQ003", CHUNKS, "EQ003")
    assert result.priority == "MEDIUM"
    assert result.category == "MAINTENANCE"
    assert result.human_approval_required is True
