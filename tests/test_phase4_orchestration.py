from datetime import datetime, timezone

from app.integration_orchestration import IntegrationOrchestrator
from app.integration_pipeline import IntegrationStore
from app.integrations import IntegrationSource, SyntheticAdapter


def sample():
    return {
        "record_type": "fault_event",
        "external_id": "F-1",
        "equipment_id": "EQ001",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "payload": {"severity": "HIGH"},
    }


def test_orchestrator_retries_transient_failure():
    adapter = SyntheticAdapter(IntegrationSource.OEM, [sample()])
    calls = {"n": 0}

    def flaky_fetch():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("temporary outage")
        return adapter.fetch()

    result = IntegrationOrchestrator(IntegrationStore(), max_attempts=3).run_source(adapter, flaky_fetch)
    assert result.status == "SUCCESS"
    assert result.attempts == 3
    assert result.accepted == 1


def test_orchestrator_does_not_retry_non_transient_logic_errors():
    adapter = SyntheticAdapter(IntegrationSource.ELD, [sample()])
    calls = {"n": 0}

    def bad_fetch():
        calls["n"] += 1
        raise RuntimeError("programming error")

    result = IntegrationOrchestrator(IntegrationStore(), max_attempts=3).run_source(adapter, bad_fetch)
    assert result.status == "FAILED"
    assert result.attempts == 1
    assert calls["n"] == 1
