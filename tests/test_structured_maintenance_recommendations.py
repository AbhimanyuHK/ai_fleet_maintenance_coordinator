from pathlib import Path
from app.phase3_retrieval import load_chunks
from app.structured_maintenance_recommendations import MaintenanceContext, generate_recommendation

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = load_chunks(ROOT / "data" / "phase3" / "knowledge")


def test_safety_context_is_critical():
    result = generate_recommendation(MaintenanceContext("EQ001", ("P-BRAKE",), ("CRITICAL",), True, 10, 0, True, True), CHUNKS)
    assert result.priority == "CRITICAL"
    assert result.human_approval_required
    assert result.evidence


def test_pm_due_within_five_days_is_high():
    result = generate_recommendation(MaintenanceContext("EQ002", (), (), False, 3, 0, False, True), CHUNKS)
    assert result.priority == "HIGH"
    assert "PM due" in " ".join(result.risk_factors)


def test_repeated_repairs_raise_priority():
    result = generate_recommendation(MaintenanceContext("EQ003", ("P-ENGINE",), ("HIGH",), False, 20, 3, False, True), CHUNKS)
    assert result.priority == "HIGH"
    assert any("Repeated" in x for x in result.risk_factors)


def test_missing_evidence_requires_review():
    result = generate_recommendation(MaintenanceContext("EQ999", ("quantum-flux",), (), False, None, 0, False, True), [] )
    assert result.priority == "REVIEW"
    assert result.evidence == ()
