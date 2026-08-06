from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from app.phase3_retrieval import KnowledgeChunk, retrieve

@dataclass(frozen=True)
class CommunicationAssessment:
    category: str
    priority: str
    safety_related: bool
    compliance_related: bool
    equipment_id: str | None
    summary: str
    draft_response: str
    evidence: tuple[str, ...]
    human_approval_required: bool = True


def assess(message: str, chunks: Iterable[KnowledgeChunk], equipment_id: str | None = None) -> CommunicationAssessment:
    text = message.lower()
    safety_terms = ("brake", "steering", "tire", "tyre", "collision", "smoke", "fire", "unsafe", "cannot stop")
    compliance_terms = ("inspection", "dot", "fmcsa", "eld", "compliance", "out of service")
    safety = any(x in text for x in safety_terms)
    compliance = any(x in text for x in compliance_terms)
    category = "SAFETY" if safety else "COMPLIANCE" if compliance else "MAINTENANCE"
    priority = "CRITICAL" if safety else "HIGH" if compliance else "MEDIUM"
    results = retrieve(message, chunks, top_k=3)
    evidence = tuple(r["chunk"].document_id for r in results)
    if safety:
        draft = "Thanks for reporting this issue. For safety reasons, please do not continue operating the equipment until Fleet Maintenance reviews the concern and confirms the next step. This response is a draft pending human approval."
    elif compliance:
        draft = "Thanks for reporting this compliance-related concern. Fleet Maintenance will review the equipment and required documentation and coordinate the next step. This response is a draft pending human approval."
    else:
        draft = "Thanks for reporting the maintenance concern. Fleet Maintenance will review the request and coordinate the appropriate service. This response is a draft pending human approval."
    summary = "Safety concern reported by driver." if safety else "Compliance concern reported by driver." if compliance else "Routine maintenance concern reported by driver."
    return CommunicationAssessment(category, priority, safety, compliance, equipment_id, summary, draft, evidence, True)
