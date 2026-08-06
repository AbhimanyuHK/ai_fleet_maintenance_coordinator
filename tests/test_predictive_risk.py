from pathlib import Path
from app.predictive_risk import RiskContext, assess_risk
from app.phase3_retrieval import load_chunks

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = load_chunks(ROOT / "data" / "phase3" / "knowledge")


def test_critical_signals_produce_critical_risk():
    result = assess_risk(RiskContext("EQ001", critical_faults=2, high_faults=1, safety_events=1, overdue_pm=True), CHUNKS)
    assert result.score >= 60
    assert result.level == "CRITICAL"
    assert result.human_approval_required


def test_medium_signals_are_proactive():
    result = assess_risk(RiskContext("EQ002", high_faults=1, recent_repairs=1), CHUNKS)
    assert result.level == "MEDIUM"
    assert result.score == 19


def test_missing_evidence_requires_review():
    result = assess_risk(RiskContext("EQ999", critical_faults=1), [])
    assert result.level == "REVIEW"
    assert result.evidence == ()
