from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Iterable
from app.phase3_retrieval import KnowledgeChunk, retrieve

@dataclass(frozen=True)
class SchedulingContext:
    equipment_id: str
    due_date: date
    proposed_date: date | None = None
    equipment_available: bool = True
    preferred_vendor: bool = True
    operational_conflict: bool = False

@dataclass(frozen=True)
class SchedulingRecommendation:
    equipment_id: str
    priority: str
    recommended_date: date | None
    recommendation: str
    reasons: tuple[str, ...]
    evidence: tuple[str, ...]
    human_approval_required: bool = True


def recommend_schedule(context: SchedulingContext, chunks: Iterable[KnowledgeChunk], today: date | None = None) -> SchedulingRecommendation:
    today = today or date.today()
    planning_days = (context.due_date - today).days
    reasons: list[str] = []
    if planning_days < 5:
        reasons.append("PM is inside the required five-day planning window")
    if not context.equipment_available:
        reasons.append("Equipment is not currently available")
    if not context.preferred_vendor:
        reasons.append("Preferred vendor/location is not selected")
    if context.operational_conflict:
        reasons.append("Proposed service conflicts with operations")
    query = "PM scheduling preventive maintenance vendor preferred location equipment availability operations"
    results = retrieve(query, chunks, top_k=3)
    evidence = tuple(r["chunk"].document_id for r in results)
    if not results:
        return SchedulingRecommendation(context.equipment_id, "REVIEW", None, "Escalate scheduling decision because approved scheduling evidence was not retrieved.", tuple(reasons) or ("No approved evidence retrieved",), (), True)
    if not context.equipment_available or context.operational_conflict:
        priority = "HIGH"
        recommendation = "Coordinate with operations and logistics to identify the earliest available low-disruption service window."
        recommended_date = None
    elif planning_days < 5:
        priority = "HIGH"
        recommendation = "Escalate immediately and schedule the earliest compliant service window; document why five-day advance planning was not possible."
        recommended_date = context.proposed_date
    else:
        priority = "MEDIUM"
        recommendation = "Schedule PM at least five days before the due date, using the preferred vendor/service location where operationally feasible."
        recommended_date = context.proposed_date
    return SchedulingRecommendation(context.equipment_id, priority, recommended_date, recommendation, tuple(reasons) or ("Five-day PM planning rule evaluated",), evidence, True)
