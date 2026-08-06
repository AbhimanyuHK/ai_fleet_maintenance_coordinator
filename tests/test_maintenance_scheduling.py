from datetime import date
from pathlib import Path
from app.maintenance_scheduling import SchedulingContext, recommend_schedule
from app.phase3_retrieval import load_chunks

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = load_chunks(ROOT / "data" / "phase3" / "knowledge")


def test_pm_is_planned_at_least_five_days_ahead():
    result = recommend_schedule(SchedulingContext("EQ001", date(2026, 8, 20), date(2026, 8, 14)), CHUNKS, date(2026, 8, 6))
    assert result.priority == "MEDIUM"
    assert result.recommended_date == date(2026, 8, 14)
    assert result.human_approval_required


def test_inside_five_day_window_is_high():
    result = recommend_schedule(SchedulingContext("EQ002", date(2026, 8, 10), date(2026, 8, 9)), CHUNKS, date(2026, 8, 6))
    assert result.priority == "HIGH"
    assert any("five-day" in r.lower() for r in result.reasons)


def test_operational_conflict_requires_coordination():
    result = recommend_schedule(SchedulingContext("EQ003", date(2026, 8, 20), date(2026, 8, 14), True, True, True), CHUNKS, date(2026, 8, 6))
    assert result.priority == "HIGH"
    assert result.recommended_date is None


def test_missing_evidence_requires_review():
    result = recommend_schedule(SchedulingContext("EQ999", date(2026, 8, 20)), [], date(2026, 8, 6))
    assert result.priority == "REVIEW"
    assert result.evidence == ()
