from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from app.phase3_retrieval import KnowledgeChunk, retrieve

@dataclass(frozen=True)
class RiskContext:
    equipment_id: str
    critical_faults: int = 0
    high_faults: int = 0
    safety_events: int = 0
    open_work_orders: int = 0
    overdue_pm: bool = False
    recent_repairs: int = 0
    unavailable: bool = False

@dataclass(frozen=True)
class RiskAssessment:
    equipment_id: str
    score: int
    level: str
    factors: tuple[str, ...]
    recommendation: str
    evidence: tuple[str, ...]
    human_approval_required: bool = True


def assess_risk(context: RiskContext, chunks: Iterable[KnowledgeChunk]) -> RiskAssessment:
    score = min(100, context.critical_faults * 25 + context.high_faults * 12 + context.safety_events * 15 + context.open_work_orders * 5 + (15 if context.overdue_pm else 0) + context.recent_repairs * 7 + (10 if context.unavailable else 0))
    factors: list[str] = []
    if context.critical_faults: factors.append(f"{context.critical_faults} critical fault(s)")
    if context.high_faults: factors.append(f"{context.high_faults} high-severity fault(s)")
    if context.safety_events: factors.append(f"{context.safety_events} safety event(s)")
    if context.open_work_orders: factors.append(f"{context.open_work_orders} open work order(s)")
    if context.overdue_pm: factors.append("Overdue PM detected")
    if context.recent_repairs: factors.append(f"{context.recent_repairs} recent repair(s)")
    if context.unavailable: factors.append("Equipment currently unavailable")
    results = retrieve("fleet failure risk safety fault maintenance PM repair", chunks, top_k=3)
    evidence = tuple(r["chunk"].document_id for r in results)
    if not results:
        return RiskAssessment(context.equipment_id, score, "REVIEW", tuple(factors) or ("No risk signals detected",), "Escalate for human review because approved evidence was not retrieved.", (), True)
    level = "CRITICAL" if score >= 60 else "HIGH" if score >= 35 else "MEDIUM" if score >= 15 else "LOW"
    if level in {"CRITICAL", "HIGH"}:
        recommendation = "Prioritize maintenance review and validate fault diagnostics, PM status, and safety implications before return to service."
    elif level == "MEDIUM":
        recommendation = "Schedule proactive inspection and monitor emerging fault and PM signals."
    else:
        recommendation = "Continue routine monitoring and preventive maintenance."
    return RiskAssessment(context.equipment_id, score, level, tuple(factors) or ("No material risk signals detected",), recommendation, evidence, True)
