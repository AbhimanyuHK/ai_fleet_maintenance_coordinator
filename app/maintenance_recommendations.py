from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.phase3_retrieval import KnowledgeChunk, retrieve


@dataclass(frozen=True)
class MaintenanceRecommendation:
    equipment_id: str
    priority: str
    recommendation: str
    reasons: tuple[str, ...]
    evidence: tuple[str, ...]
    human_approval_required: bool = True


def recommend(
    equipment_id: str,
    fault_text: str,
    driver_report: str,
    maintenance_context: str,
    chunks: Iterable[KnowledgeChunk],
) -> MaintenanceRecommendation:
    query = " ".join(filter(None, [fault_text, driver_report, maintenance_context]))
    results = retrieve(query, chunks, top_k=3)
    evidence = tuple(r["chunk"].document_id for r in results)
    safety_terms = ("brake", "steering", "tire", "tyre", "air leak", "critical")
    safety = any(term in query.lower() for term in safety_terms)
    if not results:
        return MaintenanceRecommendation(
            equipment_id=equipment_id,
            priority="REVIEW",
            recommendation="Insufficient approved knowledge evidence; escalate for human review.",
            reasons=("No approved knowledge was retrieved for the maintenance context.",),
            evidence=(),
        )
    priority = "CRITICAL" if safety else "HIGH" if fault_text.strip() else "MEDIUM"
    action = "Schedule immediate inspection before return to service." if safety else "Review and schedule the recommended maintenance action."
    return MaintenanceRecommendation(
        equipment_id=equipment_id,
        priority=priority,
        recommendation=action,
        reasons=("Maintenance context contains a fault or operational concern.", "Recommendation is grounded in retrieved approved knowledge."),
        evidence=evidence,
    )
