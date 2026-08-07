"""Policy helpers that map freshness decisions to AI workflow behavior."""
from __future__ import annotations

from dataclasses import dataclass

from app.ai_freshness_gate import FreshnessDecision


@dataclass(frozen=True)
class AIWorkflowPolicy:
    workflow: str
    allowed: bool
    status: str
    message: str


def policy_for(workflow: str, decision: FreshnessDecision) -> AIWorkflowPolicy:
    if decision.allowed:
        return AIWorkflowPolicy(
            workflow=workflow,
            allowed=True,
            status="READY",
            message="Required integration data passed the freshness gate.",
        )
    blocked = ", ".join(decision.blocking_sources) or "required sources"
    return AIWorkflowPolicy(
        workflow=workflow,
        allowed=False,
        status="BLOCKED",
        message=f"AI workflow blocked until fresh data is available for: {blocked}.",
    )


def required_sources_for(workflow: str) -> set[str]:
    """Return conservative source requirements for AI workflows.

    These are policy defaults, not claims about any vendor's API contract.
    """
    policies = {
        "maintenance_recommendation": {"TMT", "OEM", "ELD"},
        "repair_recommendation": {"OEM", "VENDOR"},
        "maintenance_scheduling": {"TMT", "ELD"},
        "predictive_risk": {"TMT", "OEM", "ELD"},
        "communication_assistant": {"TMT"},
        "knowledge_assistant": set(),
    }
    return policies.get(workflow, set())
