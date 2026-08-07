from app.ai_freshness_gate import FreshnessDecision
from app.ai_readiness_policy import policy_for, required_sources_for


def test_blocked_policy_names_blocking_sources():
    decision = FreshnessDecision(False, "BLOCKED", ("OEM", "TMT"), "stale")
    result = policy_for("predictive_risk", decision)
    assert result.allowed is False
    assert result.status == "BLOCKED"
    assert "OEM" in result.message
    assert "TMT" in result.message


def test_ready_policy_allows_workflow():
    decision = FreshnessDecision(True, "READY", (), "fresh")
    result = policy_for("maintenance_recommendation", decision)
    assert result.allowed is True
    assert result.status == "READY"


def test_workflow_source_requirements_are_conservative():
    assert required_sources_for("maintenance_recommendation") == {"TMT", "OEM", "ELD"}
    assert required_sources_for("repair_recommendation") == {"OEM", "VENDOR"}
    assert required_sources_for("maintenance_scheduling") == {"TMT", "ELD"}
    assert required_sources_for("predictive_risk") == {"TMT", "OEM", "ELD"}
    assert required_sources_for("communication_assistant") == {"TMT"}
    assert required_sources_for("knowledge_assistant") == set()
