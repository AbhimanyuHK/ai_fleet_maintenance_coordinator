from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.phase3_retrieval import KnowledgeChunk, retrieve


@dataclass(frozen=True)
class MaintenanceContext:
    equipment_id: str
    fault_codes: tuple[str, ...] = ()
    fault_severities: tuple[str, ...] = ()
    safety_related: bool = False
    pm_due_days: int | None = None
    prior_repair_count: int = 0
    driver_safety_concern: bool = False
    equipment_available: bool = True


@dataclass(frozen=True)
class StructuredRecommendation:
    equipment_id: str
    priority: str
    action: str
    risk_factors: tuple[str, ...]
    evidence: tuple[str, ...]
    human_approval_required: bool = True


def generate_recommendation(context: MaintenanceContext, chunks: Iterable[KnowledgeChunk]) -> StructuredRecommendation:
    query = " ".join(context.fault_codes + context.fault_severities + ("safety" if context.safety_related else "", "PM maintenance"))
    evidence_results = retrieve(query, chunks, top_k=3)
    evidence = tuple(r["chunk"].document_id for r in evidence_results)
    factors: list[str] = []
    if context.safety_related:
        factors.append("Safety-related fault or condition")
    if context.driver_safety_concern:
        factors.append("Driver reported a safety concern")
    if context.pm_due_days is not None and context.pm_due_days <= 5:
        factors.append(f"PM due within {context.pm_due_days} days")
    if context.prior_repair_count >= 2:
        factors.append("Repeated prior repairs detected")
    if not context.equipment_available:
        factors.append("Equipment is currently unavailable")

    if not evidence_results:
        return StructuredRecommendation(context.equipment_id, "REVIEW", "Escalate for human review because approved knowledge evidence was not retrieved.", tuple(factors) or ("No approved evidence retrieved",), (), True)
    if context.safety_related or context.driver_safety_concern:
        priority = "CRITICAL"
        action = "Schedule immediate safety inspection before return to service."
    elif context.pm_due_days is not None and context.pm_due_days <= 5:
        priority = "HIGH"
        action = "Schedule PM within the required planning window."
    elif context.prior_repair_count >= 2:
        priority = "HIGH"
        action = "Review recurring fault history and schedule diagnostic inspection."
    else:
        priority = "MEDIUM"
        action = "Review retrieved maintenance guidance and schedule the recommended service."
    return StructuredRecommendation(context.equipment_id, priority, action, tuple(factors) or ("Routine maintenance context",), evidence, True)
