from pathlib import Path
from app.phase3_retrieval import load_chunks
from app.repair_recommendations import RepairContext, recommend_repair

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = load_chunks(ROOT / "data" / "phase3" / "knowledge")

def test_estimate_variance_requires_review():
    result = recommend_repair(RepairContext("EQ001", ("P-BRAKE",), "brake repair", 0, 45000, 30000, False, True), CHUNKS)
    assert result.priority == "HIGH"
    assert result.estimate_variance == 50.0
    assert result.human_approval_required

def test_warranty_indicator_requires_warranty_review():
    result = recommend_repair(RepairContext("EQ002", ("P-ENGINE",), "engine repair", 1, 10000, 10000, True, False), CHUNKS)
    assert result.warranty_review_required is True
    assert result.priority == "HIGH"

def test_missing_evidence_is_review():
    result = recommend_repair(RepairContext("EQ999", ("unknown-fault",), "unknown issue"), [])
    assert result.priority == "REVIEW"
    assert result.evidence == ()
