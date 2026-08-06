from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from app.phase3_retrieval import KnowledgeChunk, retrieve

@dataclass(frozen=True)
class RepairContext:
    equipment_id: str
    fault_codes: tuple[str, ...] = ()
    fault_description: str = ""
    prior_repair_count: int = 0
    estimate_amount: float | None = None
    prior_estimate_amount: float | None = None
    warranty_indicator: bool = False
    vendor_additional_work: bool = False

@dataclass(frozen=True)
class RepairRecommendation:
    equipment_id: str
    priority: str
    recommendation: str
    findings: tuple[str, ...]
    evidence: tuple[str, ...]
    estimate_variance: float | None
    warranty_review_required: bool
    human_approval_required: bool = True

def recommend_repair(context: RepairContext, chunks: Iterable[KnowledgeChunk]) -> RepairRecommendation:
    query = " ".join(context.fault_codes + (context.fault_description, "repair warranty diagnostic OEM"))
    results = retrieve(query, chunks, top_k=3)
    evidence = tuple(r["chunk"].document_id for r in results)
    findings: list[str] = []
    variance = None
    if context.estimate_amount is not None and context.prior_estimate_amount not in (None, 0):
        variance = round((context.estimate_amount - context.prior_estimate_amount) / context.prior_estimate_amount * 100, 2)
        if variance > 10:
            findings.append(f"Current estimate is {variance:.1f}% above prior estimate")
    if context.vendor_additional_work:
        findings.append("Vendor reported additional work")
    if context.prior_repair_count >= 2:
        findings.append("Recurring repair history detected")
    if context.warranty_indicator:
        findings.append("Potential warranty coverage requires review")
    warranty_review = context.warranty_indicator or context.prior_repair_count >= 2
    if not results:
        return RepairRecommendation(context.equipment_id, "REVIEW", "Escalate for human review because approved repair evidence was not retrieved.", tuple(findings) or ("No approved evidence retrieved",), (), variance, warranty_review, True)
    if context.warranty_indicator or (variance is not None and variance > 10):
        priority = "HIGH"
        action = "Review diagnostic evidence, estimate justification, and warranty coverage before approving additional work."
    elif context.vendor_additional_work or context.prior_repair_count >= 2:
        priority = "HIGH"
        action = "Request diagnostic justification and review recurring repair history before approval."
    else:
        priority = "MEDIUM"
        action = "Review OEM evidence and vendor diagnostic findings before approving the proposed repair."
    return RepairRecommendation(context.equipment_id, priority, action, tuple(findings) or ("Routine repair review",), evidence, variance, warranty_review, True)
