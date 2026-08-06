from pathlib import Path

from app.maintenance_recommendations import recommend
from app.phase3_retrieval import load_chunks

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = load_chunks(ROOT / "data" / "phase3" / "knowledge")


def test_brake_issue_is_critical_and_requires_approval():
    result = recommend("EQ001", "brake fault", "driver reports poor braking", "vehicle needs service", CHUNKS)
    assert result.priority == "CRITICAL"
    assert result.human_approval_required is True
    assert result.evidence


def test_no_evidence_falls_back_to_review():
    result = recommend("EQ999", "", "", "quantum flux capacitor anomaly", CHUNKS)
    assert result.priority == "REVIEW"
    assert result.human_approval_required is True
